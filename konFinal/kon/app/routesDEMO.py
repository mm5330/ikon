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
pairs = [
    [2011,2013],
    [2011,2017],
    [2011,2015],
    [2013,2015],
    [2016,2017],
    [2015,2017],
    [2013,2016],
    [2015,2016],
    [2013,2017],
    [2017,2016],
    [2017,2015],
    [2016,2011],
    [2017,2013],
    [2017,2011],
    [2016,2015],
    [2015,2011],
    [2016,2013],
    [2015,2013],
    [2011,2016],
    [2013,2011]
]
cities = ["New York"]
voteDictionary={
    "2015":3,
    "2011":3,
    "2013":2,
    "2016":1,
    "2017":1
}

def Sortandincrease(sub_li, index, score): 
    l = len(sub_li) 
    for i in range(0, l): 
        if (sub_li[i]["id"]==index):
            sub_li[i]["score"]=score
    for i in range(0, l): 
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
        if(person.location == "New York"):
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
    if current_user.is_authenticated:
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
    finished=False
    votes = current_user.votes.all()
    if(len(votes)>=len(pairs)):
        finished=True
        first=pairs[0][0]
        second=pairs[0][1]
    else:
        first=pairs[len(votes)][0]
        second=pairs[len(votes)][1]
    return render_template('game.html', users=users, year1=first, year2=second, finished=finished)

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
    checker1=False
    checker2=False
    checker3=False
    checker4=False
    voted=False
    finished=False

    if (buttonPressed==4):
        vote = Vote(year1=first, year2=second, answer="?", author=current_user)
        db.session.add(vote)
        db.session.commit()
        votes = current_user.votes.all()
        if(len(votes)>len(pairs)):
            finished=True
        else:
            first=pairs[len(votes)][0]
            second=pairs[len(votes)][1]
        score = current_user.score
        return jsonify(users=users, year1=first, year2=second, score = score, name = current_user.username, checker1=checker1, checker2=checker2, checker3=checker3, checker4=checker4, voted=voted, finished=finished)    
    
    voted=True
    for item in nyTest[0]["temps"]:
        if(item["year"]==first):
            farm1=item["temperature"]
        if(item["year"]==second):
            farm2=item["temperature"]
    for item in nyTest[1]["temps"]:
        if(item["year"]==first):
            lag1=item["temperature"]
        if(item["year"]==second):
            lag2=item["temperature"]
    for item in nyTest[2]["temps"]:
        if(item["year"]==first):
            tet1=item["temperature"]
        if(item["year"]==second):
            tet2=item["temperature"]
    votes1=voteDictionary.get(str(first))
    votes2=voteDictionary.get(str(second))
    if(buttonPressed==1):
        print (farm1, farm2, lag1, lag2, tet1, tet2, votes1, votes2)
        vote = Vote(year1=first, year2=second, answer=str(first), author=current_user)
        db.session.add(vote)
        db.session.commit()
        if(farm1<farm2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            checker1=True
        if(lag1<lag2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            checker2=True
        if(tet1<tet2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            checker3=True
        if(votes1>votes2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            checker4=True
        voteDictionary.update({first: votes1+1})
        db.session.commit()
        Sortandincrease(users, current_user.id, current_user.score)
    if(buttonPressed==2):
        print (farm1, farm2, lag1, lag2, tet1, tet2, votes1, votes2)
        vote = Vote(year1=first, year2=second, answer=str(second), author=current_user)
        db.session.add(vote)
        db.session.commit()
        if(farm2<farm1):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            checker1=True
        if(lag2<lag1):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            checker2=True
        if(tet2<tet1):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            checker3=True
        if(votes2>votes1):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            checker4=True
        voteDictionary.update({second: votes2+1})
        db.session.commit()
        Sortandincrease(users, current_user.id, current_user.score)
    if(buttonPressed==3):
        print (farm1, farm2, lag1, lag2, tet1, tet2, votes1, votes2)
        vote = Vote(year1=first, year2=second, answer="=", author=current_user)
        db.session.add(vote)
        db.session.commit()
        if(farm1==farm2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            checker1=True
        if(lag1==lag2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            checker2=True
        if(tet1==tet2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            checker3=True
        if(votes1==votes2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            checker4=True
        db.session.commit()
        Sortandincrease(users, current_user.id, current_user.score)
    score = current_user.score
    votes = current_user.votes.all()
    if(len(votes)>=len(pairs)):
            finished=True
    else:
        first=pairs[len(votes)][0]
        second=pairs[len(votes)][1]
    score = current_user.score
    return jsonify(users=users, year1=first, year2=second, score = score, name = current_user.username, checker1=checker1, checker2=checker2, checker3=checker3, checker4=checker4, voted=voted, finished=finished)
