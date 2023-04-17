from flask import render_template, redirect, url_for, request, Blueprint, Response, jsonify, make_response, abort
from flask_login import current_user, login_user, logout_user, login_required
from .forms import LoginForm, DeployForm
from .models import User, AdminDeploy, Deployment, DeployLocation, Script, db_session, AdminProject
from .utils import *
import re
import json
from datetime import datetime
from pytz import timezone

kon = Blueprint('kon', __name__)
ERROR_JSON = {"error": "Invalid request."}


@kon.route('/', methods=['GET', 'POST'])
@kon.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    msg = request.args.get('msg', '')
    all_deployments = []
    # get all deployments for current user, name and entry code
    deployments = get_admin_deploys()
    for deploy_id in deployments:
        deployment = db_session.query(Deployment).filter_by(deploymentid=deploy_id).first()
        all_deployments.append(deployment)

    # get admin project id
    proj_dict = dict()
    for d in all_deployments:
        proj_id = d.admin_project
        if proj_dict.get(proj_id, None) is None:
            proj_dict[proj_id] = [d]
        else:
            ds = proj_dict[proj_id]
            ds.append(d)
            proj_dict[proj_id] = ds

    # list of lists of deployments separated by project ids
    proj_name_lst = list()
    proj_deploy_lst = list()
    for p in proj_dict.keys():
        proj = db_session.query(AdminProject).filter_by(project_id=p).first()
        proj_name_lst.append(proj.project_name)
        proj_deploy_lst.append(proj_dict[p])

    # return render_template('admin.html', deployments=all_deployments, msg=msg)
    return render_template('admin.html', proj_name_lst=proj_name_lst, proj_deploy_lst=proj_deploy_lst, msg=msg)


@kon.route('/dashboard/<deploy_id>#all', methods=['GET', 'POST'])
@login_required
def dashboardall(deploy_id):
    # redirect back if the deployment is not admined by the current user
    if int(deploy_id) not in get_admin_deploys():
        abort(403)

    data = dict()  # all data

    # get deployment by deploymentid
    deployment = db_session.query(Deployment).filter_by(deploymentid=deploy_id).first()
    data['deploy_name'] = deployment.deploymentname

    # overview statistics
    unique_numbers = getUniqueUserNumber(deploy_id)
    data['unique_numbers'] = unique_numbers
    if unique_numbers == 0:
        return render_template('dashboardall.html', data=data, has_user=False, deploy_id=deploy_id)

    total_responses = getTotalResponses(deploy_id)
    data['avg_responses'] = round(total_responses / unique_numbers, 2)
    max_year, min_year = getYearSpan(deployment.sat_source, deployment.station_source)
    data['num_comparison'] = (max_year - min_year + 1) ** 2

    # top players by responses bar chart
    top_resp_users, top_resp_num = getTopUserResponse(deploy_id)
    data['top_response_bar'] = top_resp_num
    data['top_response_bar_user'] = top_resp_users

    # demographic statistics
    player_ages = getAges(deploy_id)
    player_genders = getGenders(deploy_id)
    player_income = getIncomes(deploy_id)
    player_loc, player_loc_cnt = getLocations(deploy_id)
    data['age_player_bar'] = player_ages
    data['gender_player_pie'] = player_genders
    data['income_player_bar'] = player_income
    data['location_player_pie'] = player_loc
    data['location_player_pie_cnt'] = player_loc_cnt

    # top players by scores bar chart
    all_users_by_score, all_scores = getScores(deploy_id)
    data['low_score'] = min(list(filter(lambda s: s != 0, all_scores)))
    data['avg_score'] = sum(all_scores) // len(all_scores)
    data['high_score'] = max(all_scores)
    top_scores = all_scores[:10]
    top_score_users = all_users_by_score[:10]
    top_scores.reverse()
    top_score_users.reverse()
    data['score_player_bar'] = top_scores
    data['score_player_bar_user'] = top_score_users

    # referral bar chart
    all_referrers, all_referee_num = getUserReferrals(deploy_id)
    total_referee_num = sum(all_referee_num)
    data['player_referred'] = total_referee_num
    data['player_referred_percent'] = round((total_referee_num / unique_numbers) * 100, 2)
    top_referrers = all_referrers[:10]
    top_referee_num = all_referee_num[:10]
    top_referrers.reverse()
    top_referee_num.reverse()
    data['referral_player_bar'] = top_referee_num
    data['referral_player_bar_user'] = top_referrers

    # year comparison heat map
    year_comparisons = getYearComparisons(deploy_id)
    year_comparisons_data = []
    all_years = list(range(min_year, max_year+1))
    for i in all_years:
        for j in all_years:
            num_resp = year_comparisons.get((i, j), 0)
            year_comparisons_data.append(num_resp)
    data['year_comparison_years'] = all_years
    data['year_comparison_comparisons'] = year_comparisons_data

    return render_template('dashboardall.html', data=data, has_user=True, deploy_id=deploy_id)


@kon.route('/dashboard/<deploy_id>#after', methods=['GET', 'POST'])
@login_required
def dashboardafter(deploy_id):
    # redirect back if the deployment is not admined by the current user
    if int(deploy_id) not in get_admin_deploys():
        abort(403)

    data = dict()  # data After start date

    # get deployment by deploymentid
    deployment = db_session.query(Deployment).filter_by(deploymentid=deploy_id).first()
    # get the start time of the deployment
    tz = timezone('EST')
    start_date_time = datetime.combine(deployment.start_date, datetime.min.time(), tz)

    data['deploy_name'] = deployment.deploymentname

    # overview statistics
    unique_numbers = getUniqueUserNumberAfter(deploy_id, start_date_time)
    data['unique_numbers'] = unique_numbers
    if unique_numbers == 0:
        return render_template('dashboardafter.html', data=data, has_user_after=False, deploy_id=deploy_id)

    total_responses = getTotalResponsesAfter(deploy_id, start_date_time)
    data['avg_responses'] = round(total_responses / unique_numbers, 2)
    max_year, min_year = getYearSpan(deployment.sat_source, deployment.station_source)
    data['num_comparison'] = (max_year - min_year + 1) ** 2

    # top players by responses bar chart
    top_resp_users, top_resp_num = getTopUserResponseAfter(deploy_id, start_date_time)
    data['top_response_bar'] = top_resp_num
    data['top_response_bar_user'] = top_resp_users

    # demographic statistics
    player_ages = getAgesAfter(deploy_id, start_date_time)
    player_genders = getGendersAfter(deploy_id, start_date_time)
    player_income = getIncomesAfter(deploy_id, start_date_time)
    player_loc, player_loc_cnt = getLocationsAfter(deploy_id, start_date_time)
    data['age_player_bar'] = player_ages
    data['gender_player_pie'] = player_genders
    data['income_player_bar'] = player_income
    data['location_player_pie'] = player_loc
    data['location_player_pie_cnt'] = player_loc_cnt

    # top players by scores bar chart
    all_users_by_score, all_scores = getScoresAfter(deploy_id, start_date_time)
    data['low_score'] = min(list(filter(lambda s: s != 0, all_scores)))
    data['avg_score'] = sum(all_scores) // len(all_scores)
    data['high_score'] = max(all_scores)
    top_scores = all_scores[:10]
    top_score_users = all_users_by_score[:10]
    top_scores.reverse()
    top_score_users.reverse()
    data['score_player_bar'] = top_scores
    data['score_player_bar_user'] = top_score_users

    # referral bar chart
    all_referrers, all_referee_num = getUserReferralsAfter(deploy_id, start_date_time)
    total_referee_num = sum(all_referee_num)
    data['player_referred'] = total_referee_num
    data['player_referred_percent'] = round((total_referee_num / unique_numbers) * 100, 2)
    top_referrers = all_referrers[:10]
    top_referee_num = all_referee_num[:10]
    top_referrers.reverse()
    top_referee_num.reverse()
    data['referral_player_bar'] = top_referee_num
    data['referral_player_bar_user'] = top_referrers

    # year comparison heat map
    year_comparisons = getYearComparisonsAfter(deploy_id, start_date_time)
    year_comparisons_data = []
    all_years = list(range(min_year, max_year+1))
    for i in all_years:
        for j in all_years:
            num_resp = year_comparisons.get((i, j), 0)
            year_comparisons_data.append(num_resp)
    data['year_comparison_years'] = all_years
    data['year_comparison_comparisons'] = year_comparisons_data

    return render_template('dashboardafter.html', data=data, has_user_after=True, deploy_id=deploy_id)


@kon.route('/responses_download/<deploy_code>', methods=['GET', 'POST'])
@login_required
def responses_download(deploy_code):
    # get deployment info by entry code (input arg)
    d = db_session.query(Deployment).filter_by(entry_code=deploy_code).first()

    # redirect back if the deployment is not admined by the current user
    if int(d.deploymentid) not in get_admin_deploys():
        abort(403)

    csv = getResponsesCSV(d.deploymentid)
    filename = d.deploymentname.replace(' ', '_')
    header_content = 'attachment; filename=%s.csv' % filename
    return Response(
        csv,
        mimetype='text/csv',
        headers={'Content-disposition': header_content})


@kon.route('/edit/<deploy_code>', methods=['GET', 'POST'])
@login_required
def edit(deploy_code):
    update_msg = ''
    # return to deployment table if cancel clicked
    if 'cancel' in request.form:
        return redirect(url_for('kon.admin', msg=update_msg))
    # number of rows for location list
    num_locations = 1
    deploy_form = DeployForm(request.form)
    # get deployment info by entry code (input arg)
    d = db_session.query(Deployment).filter_by(entry_code=deploy_code).first()
    deploy_id = d.deploymentid
    deployment_project_name = getProjectNameById(d.admin_project)

    # redirect back if the deployment is not admined by the current user
    if int(deploy_id) not in get_admin_deploys():
        abort(403)

    # get location list
    deploy_locations = ''
    d_locations = db_session.query(DeployLocation).filter_by(deploymentid=deploy_id).order_by(DeployLocation.listorder)
    for loc in d_locations:
        deploy_locations += loc.location + '\r\n'
        num_locations += 1
    deploy_form.location_list.data = deploy_locations

    # get deployment current language
    d_script = db_session.query(Script).filter_by(script_name=d.script_name).first()
    d_language = d_script.language

    # get all language options
    lang_options = getScripts()
    deploy_form.language_select.choices = lang_options
    deploy_form.language_select.data = d_language

    # get start and end date
    deploy_form.end_date.data = d.end_date
    deploy_form.start_date.data = d.start_date

    # gamification option
    deploy_form.gamification_select.choices = getGamificationOptions()
    deploy_form.gamification_select.data = str(d.gamification)

    # get all data source options
    source_arr, sat_options, wea_options = getDataSources()
    deploy_form.sat_select.choices = sat_options
    deploy_form.sat_select.data = d.sat_source
    deploy_form.wea_select.choices = wea_options
    deploy_form.wea_select.data = d.station_source

    # get all existing project names
    project_names = getProjectName()

    # POST
    if request.method == 'POST':
        if 'confirm' in request.form:
            # get project id by project name
            project_name = request.form['project_name']
            d.admin_project = getProjectIdByName(project_name)
            # update deployment name
            d.deploymentname = request.form['deploy_name']
            # update location list
            locations = request.form['location_list']
            updateLocationList(locations, deploy_id, d_locations)
            # update deployment script
            deploy_language = request.form['language_select']
            deploy_script = db_session.query(Script).filter_by(language=deploy_language).first()
            d.script_name = deploy_script.script_name
            # update start and end date
            d.start_date = request.form['start_date']
            d.end_date = request.form['end_date']
            # update gamification option
            d.gamification = int(request.form['gamification_select'])
            # update data sources
            d.sat_source = request.form['sat_select']
            d.station_source = request.form['wea_select']
            db_session.commit()
            # check whether entry code include alphabetic characters only
            code = re.search("^[a-zA-Z]+$", request.form['entry_code'])
            if code:
                d.entry_code = request.form['entry_code']
                db_session.commit()
                update_msg = 'You have successfully updated deployment: ' + d.deploymentname
            else:
                # highlight entry code message
                return render_template('edit.html', form=deploy_form,
                                       deployment=d, num_locations=str(num_locations),
                                       valid_entry_code=False, sources=source_arr,
                                       deployment_project_name=deployment_project_name, project_names=project_names)
        return redirect(url_for('kon.admin', msg=update_msg))
    # GET
    return render_template('edit.html', form=deploy_form,
                           deployment=d, num_locations=str(num_locations),
                           valid_entry_code=True, sources=source_arr,
                           deployment_project_name=deployment_project_name, project_names=project_names)


@kon.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    update_msg = ''
    deploy_form = DeployForm(request.form)

    # get all language options
    lang_options = getScripts()
    deploy_form.language_select.choices = lang_options

    # gamification option
    deploy_form.gamification_select.choices = getGamificationOptions()

    # get all data source options
    source_arr, sat_options, wea_options = getDataSources()
    deploy_form.sat_select.choices = sat_options
    deploy_form.wea_select.choices = wea_options

    # get all existing project names
    project_names = getProjectName()

    # POST
    if request.method == 'POST':
        if 'create' in request.form:
            # project name
            project_name = request.form['project_name']
            # deployment name
            deploy_name = request.form['deploy_name']
            # deployment script
            deploy_language = request.form['language_select']
            deploy_script = db_session.query(Script).filter_by(language=deploy_language).first()
            script_name = deploy_script.script_name
            # deployment start and end date
            deploy_start_date = request.form['start_date']
            deploy_end_date = request.form['end_date']
            # gamification setting
            deploy_gamification = int(request.form['gamification_select'])
            # data sources
            sat_source = request.form['sat_select']
            station_source = request.form['wea_select']
            # check whether entry code valid
            entry_code = request.form['entry_code']
            # include alphabetic characters only
            code = re.search("^[a-zA-Z]+$", entry_code)
            # uniqueness
            same_code = db_session.query(Deployment).filter_by(entry_code=entry_code).first()
            if code and (not same_code):
                # create a new deployment if valid entry code
                d = createDeployment(deploy_name, script_name, sat_source, station_source,
                                     deploy_end_date, deploy_start_date, deploy_gamification, entry_code, project_name)
                db_session.commit()
                deploy_id = d.deploymentid
                # update location list
                locations = request.form['location_list']
                updateLocationList(locations, deploy_id, [])
                update_msg = 'You have successfully created deployment: ' + d.deploymentname
            else:
                # highlight entry code message
                return render_template('create.html', form=deploy_form, valid_entry_code=False,
                                       sources=source_arr, project_names=project_names)
        return redirect(url_for('kon.admin', msg=update_msg))
    # GET
    return render_template('create.html', form=deploy_form, valid_entry_code=True,
                           sources=source_arr, project_names=project_names)


@kon.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        # read form data
        username = request.form['username']
        password = request.form['password']
        # Locate user
        user = db_session.query(User).filter_by(admin_name=username).first()
        # Check the password
        if user is not None:
            if password == user.password:
                login_user(user)
                return redirect(url_for('kon.admin'))
        # Something (user or pass) is not ok
        return render_template('login.html', msg='Wrong username or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template('login.html', form=login_form)
    return redirect(url_for('kon.admin'))


@kon.route('/editor/<deploy_code>', methods=['GET', 'POST'])
@login_required
def editor(deploy_code):
    d = db_session.query(Deployment).filter_by(entry_code=deploy_code).first()

    # redirect back if the deployment is not admined by the current user
    if int(d.deploymentid) not in get_admin_deploys():
        abort(403)

    script_name = d.script_name
    script = db_session.query(Script).filter_by(script_name=script_name).first()
    return render_template('scripteditor.html', script=script, deploy_code=deploy_code)


@kon.route('/script_edit', methods=['GET', 'POST'])
@login_required
def script_edit():
    if not is_json_request(request, ['script', 'deploy_code']):
        return jsonify(ERROR_JSON), 400
    body = request.get_json()
    script_content = json.dumps(body['script'])
    deploy_code = body['deploy_code']
    d = db_session.query(Deployment).filter_by(entry_code=deploy_code).first()
    script_name_name = d.script_name
    deploy_id = d.deploymentid
    script = db_session.query(Script).filter_by(script_name=script_name_name).first()
    script_lang_name = script.language
    script_lang = getMainName(script_lang_name) + '-' + str(deploy_id)
    script_name = getMainName(script_name_name) + '-' + str(deploy_id)
    script_with_lang = db_session.query(Script).filter_by(script_name=script_name).first()
    # if the language script already existed for the deployment
    if script_with_lang:
        script_with_lang.content = script_content
        db_session.commit()
    # if not exist, create new
    else:
        addScript(script_name, script_content, script_lang)
    d.script_name = script_name
    db_session.commit()
    update_msg = 'You have successfully updated the language script for deployment: ' + d.deploymentname
    return make_response(update_msg, 200)


@kon.route('/datasource', methods=['GET', 'POST'])
@login_required
def datasource():
    return render_template('datasource.html')


@kon.route('/source_sample/<sample_name>', methods=['GET', 'POST'])
@login_required
def source_sample(sample_name):
    filename = 'source_%s.csv' % sample_name
    with open('app/static/assets/' + filename) as fp:
        csv = fp.read()
    return Response(
        csv,
        mimetype='text/csv',
        headers={'Content-disposition': ('attachment; filename=' + filename)})


@kon.route('/source_download/<source_name>', methods=['GET', 'POST'])
@login_required
def source_download(source_name):
    csv = getDataSourceCSV(source_name)
    filename = source_name.replace(' ', '_')
    header_content = 'attachment; filename=%s.csv' % filename
    return Response(
        csv,
        mimetype='text/csv',
        headers={'Content-disposition': header_content})


@kon.route('/source_upload', methods=['GET', 'POST'])
@login_required
def source_upload():
    if not is_json_request(request, ['source_data', 'source_name', 'source_type',
                                     'source_country', 'source_region', 'source_description']):
        return jsonify(ERROR_JSON), 400
    body = request.get_json()
    # check csv data types and remove duplicates
    source_data = checkCsvDataType(body['source_data'])
    if source_data is None:
        return make_response('Failed: Please ensure that you have the correct data types in the file.', 400)
    # check if data source existed and its owner
    source_name = body['source_name']
    source_with_name = db_session.query(DataSource).filter_by(source_name=source_name).first()
    if source_with_name:
        source_owner = source_with_name.owner
        if source_owner != current_user.admin_id:
            return make_response(
                'Failed: The data source "%s" already existed. Please use a different name.' % source_name, 400)
        else:
            # overwrite the old data
            deleteSourceByName(source_name)
    # add data source meta data
    addDataSource(source_name, body['source_type'], body['source_country'], body['source_region'],
                  body['source_description'], source_with_name)
    # insert all rows in the csv file
    for row in source_data:
        data_year = row[0]
        data_value = row[1]
        insertDataOfSource(data_year, data_value, source_name)
    # success message
    update_msg = 'Data source uploaded successfully!'
    return make_response(update_msg, 200)


@kon.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('kon.login'))


# register currently disabled
@kon.route('/register', methods=['GET', 'POST'])
def register():
    return redirect(url_for('kon.login'))


@kon.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')


@kon.route('/info', methods=['GET', 'POST'])
def info():
    return render_template('info.html')


@kon.route('/video', methods=['GET', 'POST'])
def video():
    return render_template('video.html')


# page not found error handling
@kon.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('page-404.html'), 404


# server error handling
@kon.errorhandler(500)
def server_error(e):
    return render_template('page-500.html'), 500


# Access denied error handling
@kon.errorhandler(403)
def access_denied_error(e):
    return render_template('page-403.html'), 403


# get a list of all deployment ids admined by the current user
def get_admin_deploys():
    all_deploymentid = []
    admin_id = current_user.admin_id
    # get all deployments for current user, name and entry code
    deployments = db_session.query(AdminDeploy).filter_by(admin_id=admin_id)
    for d in deployments:
        all_deploymentid.append(d.deploymentid)
    return all_deploymentid


# Google report dashboard
# @kon.route('/dashboard/<deploy_code>', methods=['GET', 'POST'])
# @login_required
# def dashboard(deploy_code):
#     # access permission needed (anyone with link can view)
#     if deploy_code == 'tecnicafe':
#         report_url = 'https://datastudio.google.com/embed/reporting/06158183-56b3-43e4-9c8d-f5a8786e36d2/page/5VbBC'
#     else:
#         report_url = 'https://datastudio.google.com/embed/reporting/664af251-b419-46f4-b9c5-cd14897996ea/page/DjD'
#     return render_template('dashboard(google).html', report_url=report_url)
