from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Vote
from werkzeug.urls import url_parse
from sqlalchemy import update
import csv, random

users =[
]
sameplace =[
]
years =[
]
year1=2000
year2=2001
yearDictionary = dict()
cities = [
]
with open('years.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            yearAndScore ={
                "year": row["Year"],
                "value": row["Value"]
            }
            if row["Region"] not in cities:
                cities.append(row["Region"])
            if (yearDictionary.get(row["Source Type"])==None):
                yearDictionary.setdefault(row["Source Type"], dict())
            if ((yearDictionary.get(row["Source Type"])).get(row["Region"])==None):
                (yearDictionary.get(row["Source Type"])).setdefault(row["Region"], [])
            (yearDictionary.get(row["Source Type"])).get(row["Region"]).append(yearAndScore)
            line_count += 1
voteDictionary = dict()
votes = Vote.query.all()
for vote in votes:
    if (vote.answer != "?" and vote.answer != "="):
        year = int(vote.answer)
        if (voteDictionary.get(vote.author.location)==None):
            voteDictionary.setdefault(vote.author.location, dict())
        if(voteDictionary.get(vote.author.location).get(year)==None):
            voteDictionary.get(vote.author.location).setdefault(year, 1)
        else:
            score = voteDictionary.get(vote.author.location).get(year)
            voteDictionary.get(vote.author.location).update({year: score+1})

def Sortandincrease(sub_li, index): 
    l = len(sub_li) 
    for i in range(0, l): 
        if (sub_li[i]["id"]==index):
            sub_li[i]["score"]+=50
        for j in range(0, l-i-1): 
            if (sub_li[j]["score"] < sub_li[j + 1]["score"]): 
                tempo = sub_li[j] 
                sub_li[j]= sub_li[j + 1] 
                sub_li[j + 1]= tempo 
    return sub_li 

def Sort(sub_li):
    l = len(sub_li) 
    for i in range(0, l): 
        for j in range(0, l-i-1): 
            if (sub_li[j]["score"] < sub_li[j + 1]["score"]): 
                tempo = sub_li[j] 
                sub_li[j]= sub_li[j + 1] 
                sub_li[j + 1]= tempo 
    return sub_li 

nyTest= [
    {
        "name":"Farmingdale Republic Airport",
        "temps":
        [
            {
                "year":2011,
                "temperature":30.37
            },
            {
                "year":2013,
                "temperature":35.83
            },
            {
                "year":2015,
                "temperature":30.73
            },
            {
                "year":2016,
                "temperature":40.30
            },
            {
                "year":2017,
                "temperature":37.77
            }
        ]
    },
    {
        "name":"Laguardia Airport",
        "temps":
        [
            {
                "year":2011,
                "temperature":34.47
            },
            {
                "year":2013,
                "temperature":37.67
            },
            {
                "year":2015,
                "temperature":31.60
            },
            {
                "year":2016,
                "temperature":41.63
            },
            {
                "year":2017,
                "temperature":40.93
            }
        ]
    },
    {
        "name":"Teterboro Airport",
        "temps":
        [
            {
                "year":2011,
                "temperature":31.07
            },
            {
                "year":2013,
                "temperature":36.00
            },
            {
                "year":2015,
                "temperature":30.00
            },
            {
                "year":2016,
                "temperature":39.73
            },
            {
                "year":2017,
                "temperature":38.67
            }
        ]
    }
]

@app.before_request
def before_request():
    global users
    users=[]
    current = User.query.all()
    for person in current:
        user = {
            "id": person.id,
            "name": person.username,
            "score": person.score,
            "location": person.location
        }
        users.append(user)
    Sort(users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    global sameplace
    sameplace = []
    if current_user.is_authenticated:
        for user in users:
            if (user["location"]==current_user.location):
                sameplace.append(user)
        return redirect(url_for('game'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        for user in users:
            if (user["location"]==current_user.location):
                sameplace.append(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('game')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('game'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    global cities
    if current_user.is_authenticated:
        return redirect(url_for('game'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, score =0, location = form.location.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, cities=cities)

@app.route('/')
@app.route('/game')
@login_required
def game():
    global year1
    global year2
    if not sameplace:
        for user in users:
            if (user["location"]==current_user.location):
                sameplace.append(user)
    votes = current_user.votes.all()
    found = True
    while (found):
        found = False
        first = random.randint(2000, 2019)
        second = random.randint(2000, 2019)
        if(first == second):
            if (first==2019):
                second= random.randint(2000, 2018)
            else:
                second=second+1
        for vote in votes:
            if (vote.year1 == first and vote.year2 == second):
                found = True
                break
    return render_template('game.html', users=sameplace, year1=first, year2=second)

@app.route('/button', methods=['GET', 'POST'])
def button():
    global users
    global years
    global year1
    global year2

    json_data = request.get_json()
    buttonPressed = int(json_data["button"])
    first = int(json_data["year1"])
    second = int(json_data["year2"])
    stationChecker=False
    satChecker=False
    voteChecker=False
    voted=False

    if (buttonPressed==4):
        vote = Vote(year1=first, year2=second, answer="?", author=current_user)
        db.session.add(vote)
        db.session.commit()
        votes = current_user.votes.all()
        found = True
        while (found):
            found = False
            first = random.randint(2000, 2019)
            second = random.randint(2000, 2019)
            if(first == second):
                if (first==2019):
                    second= random.randint(2000, 2018)
                else:
                    second=second+1
            for vote in votes:
                if (vote.year1 == first and vote.year2 == second):
                    found = True
                    break
        score = current_user.score
        return jsonify(users=sameplace, year1=first, year2=second, score = score, name = current_user.username, satChecker=satChecker, stationChecker=stationChecker, voteChecker=voteChecker, voted=voted)    
    
    voted=True
    weather1 = 0
    weather2 = 0
    rainfall1=0
    rainfall2=0
    votes1=voteDictionary.get(current_user.location).get(first, -1)
    votes2=voteDictionary.get(current_user.location).get(second, -1)
    for year in yearDictionary.get("Weather Station").get(current_user.location):
        if (int(year["year"])==first):
            weather1 = int(year["value"])
        if (int(year["year"])==second):
            weather2 = int(year["value"])
    for year in yearDictionary.get("Rainfall").get(current_user.location):
        if (int(year["year"])==first):
            rainfall1 = int(year["value"])
        if (int(year["year"])==second):
            rainfall2 = int(year["value"])
    if(buttonPressed==1):
        print (weather1, weather2, rainfall1, rainfall2, votes1, votes2)
        vote = Vote(year1=first, year2=second, answer=str(first), author=current_user)
        db.session.add(vote)
        db.session.commit()
        if(rainfall1>rainfall2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            satChecker=True
        if(weather1>weather2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            stationChecker=True
        if(votes1>votes2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            voteChecker=True
        voteDictionary.get(current_user.location).update({first: votes1+1})
        db.session.commit()
        Sortandincrease(sameplace, current_user.id)
    if(buttonPressed==2):
        print (weather1, weather2, rainfall1, rainfall2)
        vote = Vote(year1=first, year2=second, answer=str(second), author=current_user)
        db.session.add(vote)
        db.session.commit()
        if(rainfall2>rainfall1):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            satChecker=True
        if(weather2>weather1):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            stationChecker=True
        if(votes2>votes1):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            voteChecker=True
        voteDictionary.get(current_user.location).update({second: votes2+1})
        db.session.commit()
        Sortandincrease(sameplace, current_user.id)
    if(buttonPressed==3):
        print (weather1, weather2, rainfall1, rainfall2)
        vote = Vote(year1=first, year2=second, answer="=", author=current_user)
        db.session.add(vote)
        db.session.commit()
        if(rainfall1==rainfall2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            satChecker=True
        if(weather1==weather2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            stationChecker=True
        if(votes1==votes2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            voteChecker=True
        db.session.commit()
        Sortandincrease(sameplace, current_user.id)
    votes = current_user.votes.all()
    found = True
    while (found):
        found = False
        first = random.randint(2000, 2019)
        second = random.randint(2000, 2019)
        if(first == second):
            if (first==2019):
                second= random.randint(2000, 2018)
            else:
                second=second+1
        for vote in votes:
            if (vote.year1 == first and vote.year2 == second):
                found = True
                break
    score = current_user.score

    return jsonify(users=sameplace, year1=first, year2=second, score = score, name = current_user.username, satChecker=satChecker, stationChecker=stationChecker, voteChecker=voteChecker, voted=voted)
