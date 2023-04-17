from flask import render_template, flash, redirect, url_for, request, jsonify, Blueprint, session
from .forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from .utils import *
from .database import *


kon = Blueprint('kon', __name__)


@kon.route('/login', methods=['GET', 'POST'])
def login():
    # if their login works and sends them to the game page
    if current_user.is_authenticated:
        return redirect(url_for('kon.game'))

    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        user_db = getUserByUsername(user_name)

        # sends error message if not logged in correctly
        if not user_db:
            flash('Invalid username')
            return redirect(url_for('kon.login'))

        user_id = getUserId(user_name)
        user_info_update(user_id)
        user = user_info_initialize(user_id)
        print("user: ", user)

        # logs in user and sends them to next page or game
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('kon.game')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


# logout route
@kon.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('kon.game'))


# registration page route
@kon.route('/register', methods=['GET', 'POST'])
def register():
    # automatically sent to game if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('kon.game'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user_id = form.email.data
        user_name = form.username.data
        entry_code = form.entry_code.data[:5]
        referral_code = form.entry_code.data[5:]
        # TODO: add referral code logic
        user_deploy = getDeployByCode(entry_code)
        # if form submitted correctly then new user is created and added to database and user is sent to login
        # generate unique referral code
        user_code = generate_code(6)
        while getUserByCode(user_code):
            user_code = generate_code(6)
        insertUser(user_id, user_name, 0, user_deploy, user_code)
        # get message script file for the deployment
        script_dict = getScript(user_deploy, "web")
        flash(script_dict["register_success"])
        return redirect(url_for('kon.login'))

    return render_template('register.html', title='Register', form=form)


@kon.route('/', methods=['GET', 'POST'])
@kon.route('/game', methods=['GET', 'POST'])
@login_required
def game():
    print("(game) current_user: ", current_user)
    user_id = current_user.get_id()
    deploy_years = current_user.get_deploy_years()
    question_years = generateTwoYears(user_id, deploy_years)
    # question generated
    if question_years:
        question_year_1 = question_years[0]
        question_year_2 = question_years[1]
        deploy_users = current_user.get_deploy_users()
        script_dict = current_user.get_script_dict()

        return render_template('game.html', script_dict=script_dict,
                               users=deploy_users, year1=question_year_1, year2=question_year_2)

    # question exhausted
    # TODO: ADD


@kon.route('/button', methods=['GET', 'POST'])
def button():
    # initialize default values (for "dont know" button)
    voted = False
    satChecker = False
    stationChecker = False
    voteChecker = False
    satName = None
    stationName = None
    voteCount = None

    print("(button) CALLED")
    user_id = current_user.get_id()
    user_name = current_user.get_username()
    user_score = current_user.get_score()
    deployment_id = current_user.get_deployment()
    sat_source_name = current_user.get_sat_source_name()
    station_source_name = current_user.get_station_source_name()
    deploy_years = current_user.get_deploy_years()

    neighbor_weight = getNeighborWeights(deployment_id)
    sat_source_weight = (100 - neighbor_weight) / 2
    station_source_weight = sat_source_weight

    json_data = request.get_json()
    buttonPressed = int(json_data["button"])  # 1 for year1, 2 for year2, 3 for same, 4 for unknown
    question_year_1 = int(json_data["year1"])
    question_year_2 = int(json_data["year2"])

    if buttonPressed:
        print("buttonPressed = ", buttonPressed)
        answer = buttonPressed
        # insert user response to database
        insertResponse(user_id, question_year_1, question_year_2, answer)

        if answer != 4:  # voted
            voted = True
            points = user_score
            # get actual satellite and weather station data for each year
            sat_data_1 = getSatValue(sat_source_name, question_year_1)
            sat_data_2 = getSatValue(sat_source_name, question_year_2)
            station_data_1 = getSatValue(station_source_name, question_year_1)
            station_data_2 = getSatValue(station_source_name, question_year_2)
            # answer based on satellite and weather station data
            sat_answer = getAnswer(sat_data_1, sat_data_2)
            station_answer = getAnswer(station_data_1, station_data_2)

            # match with satellite data
            if sat_answer == answer:
                satChecker = True
                satName = sat_source_name
                points += sat_source_weight
            # match with weather station data
            if station_answer == answer:
                stationChecker = True
                stationName = station_source_name
                points += station_source_weight
            # match with other user responses in the deployment
            deploy_responses = getDeployResponses(question_year_1, question_year_2, deployment_id)
            if deploy_responses:
                responses_matched = deploy_responses.count(answer)
                voteCount = responses_matched
                if responses_matched > 0:
                    voteChecker = True
                    points += responses_matched * neighbor_weight

            # update user score
            print("updated user points: ", points)
            setUserScore(user_id, points)
            current_user.set_score(points)
            current_user.set_deploy_users(update_deploy_users(deployment_id))

            # generate two new years for the next question
            question_years = generateTwoYears(user_id, deploy_years)

            # TODO: ADD
            # if question exhausted


            question_year_1 = question_years[0]
            question_year_2 = question_years[1]

    user_score = current_user.get_score()
    deploy_users = current_user.get_deploy_users()
    script_dict = current_user.get_script_dict()

    return jsonify(script_dict=script_dict, users=deploy_users,
                   year1=question_year_1, year2=question_year_2, score=user_score, name=user_name,
                   satChecker=satChecker, stationChecker=stationChecker, voteChecker=voteChecker, voted=voted,
                   satName=satName, stationName=stationName, voteCount=voteCount)


@kon.route('/info/', defaults={'lang': None})
@kon.route('/info/<lang>')
def info(lang):
    if lang == 'es':
        doc_name = "InformationSheetSpanish"
    else:
        doc_name = "InformationSheetEnglish"
    return render_template('info.html', doc_name=doc_name)
