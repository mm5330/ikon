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
year1=2004
year2=2005
yearDictionary = dict()
cities = [
]

#sets up dictionary on start to keep year data for satellite and weather station. dictionary is set up by source type then city and in each city dictionary there are variable holding year and score. typeif new city encountered, also added to cities list
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

#sets up dictionary to hold votes in. dictionary set up by location then the 2 years compared and then each answer has a number of times responded
voteDictionary = dict()
votes = Vote.query.all()
for vote in votes:
    yearDuo = str(max(vote.year1, vote.year2))+","+str(min(vote.year1,vote.year2))
    if (voteDictionary.get(vote.author.location)==None):
        voteDictionary.setdefault(vote.author.location, dict())
    if(voteDictionary.get(vote.author.location).get(yearDuo)==None):
        voteDictionary.get(vote.author.location).setdefault(yearDuo, dict())
        voteDictionary.get(vote.author.location).get(yearDuo).setdefault(vote.answer, 1)
    elif (voteDictionary.get(vote.author.location).get(yearDuo).get(vote.answer)==None):
        voteDictionary.get(vote.author.location).get(yearDuo).setdefault(vote.answer, 1)
    else:
        score = voteDictionary.get(vote.author.location).get(yearDuo).get(vote.answer)
        voteDictionary.get(vote.author.location).get(yearDuo).update({vote.answer: score+1})

#sorts index of sub_li by score after increasing score of user at the index given
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

#sorts index of sub_li
def Sort(sub_li):
    l = len(sub_li) 
    for i in range(0, l): 
        for j in range(0, l-i-1): 
            if (sub_li[j]["score"] < sub_li[j + 1]["score"]): 
                tempo = sub_li[j] 
                sub_li[j]= sub_li[j + 1] 
                sub_li[j + 1]= tempo 
    return sub_li 

#when anyone connects to the server, a list of users is reupdated from the database
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

#route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    global sameplace
    sameplace = []
    #creates list of users that are in the same place as current user if their login works and sends them to the game page
    if current_user.is_authenticated:
        for user in users:
            if (user["location"]==current_user.location):
                sameplace.append(user)
        return redirect(url_for('game'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        #sends error message if not logged in correctly 
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        #logs in user and sends them to next page or game    
        login_user(user, remember=form.remember_me.data)
        for user in users:
            if (user["location"]==current_user.location):
                sameplace.append(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('game')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)

#logout route
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('game'))

#registration page route
@app.route('/register', methods=['GET', 'POST'])
def register():
    global cities
    #automatically sent to game if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('game'))


    form = RegistrationForm()
    if form.validate_on_submit():
        #if form submittd correctly then new user is created and added to database and user is sent to login
        user = User(username=form.username.data, email=form.email.data, score =0, location = form.location.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form, cities=cities)

#actual game route
@app.route('/')
@app.route('/game')
@login_required
def game():
    global year1
    global year2

    #creates sameplace list if not already there
    if not sameplace:
        for user in users:
            if (user["location"]==current_user.location):
                sameplace.append(user)
    
    #randomly decides 2 years within range of 2000 and 2019 and checks if user has already answered years in that order - if so, finds 2 random years again and again until it is new to user and then sends the user those years to ask
    votes = current_user.votes.all()
    found = True
    while (found):
        found = False
        first = random.randint(2004, 2019)
        second = random.randint(2004, 2019)
        if(first == second):
            if (first==2019):
                second= random.randint(2004, 2018)
            else:
                second=second+1
        for vote in votes:
            if (vote.year1 == first and vote.year2 == second):
                found = True
                break
    return render_template('game.html', users=sameplace, year1=first, year2=second)

#interaction between front end and backend when user clicks a button to make a vote
@app.route('/button', methods=['GET', 'POST'])
def button():
    global users
    global years
    global year1
    global year2

    #retrieves json data from javascript (2 years and button picked) and sets up variables for them
    json_data = request.get_json()
    buttonPressed = int(json_data["button"])
    first = int(json_data["year1"])
    second = int(json_data["year2"])

    #booleans for checking if user answered correctly and/or at all (used later)
    stationChecker=False
    satChecker=False
    voteChecker=False
    voted=False

    #years set up to easily search in database
    couple = str(max(first, second))+","+str(min(first,second))
    
    #total number of votes to easily calculate percentage of users which user agrees with
    total=0

    #for user choosing "I don't know"
    if (buttonPressed==4):
        #adds vote to database
        vote = Vote(year1=first, year2=second, answer="?", author=current_user)
        db.session.add(vote)
        db.session.commit()

        #finds next 2 years to ask user
        votes = current_user.votes.all()
        found = True
        while (found):
            found = False
            first = random.randint(2004, 2019)
            second = random.randint(2004, 2019)
            if(first == second):
                if (first==2019):
                    second= random.randint(2004, 2018)
                else:
                    second=second+1
            for vote in votes:
                if (vote.year1 == first and vote.year2 == second):
                    found = True
                    break

        score = current_user.score

        #adds new vote to proper voteDictionary spot and creates one if there wasn't
        if(voteDictionary.get(current_user.location).get(couple)==None):
            voteDictionary.get(current_user.location).setdefault(couple, dict())
            voteDictionary.get(current_user.location).get(couple).setdefault("?", 1)
        elif (voteDictionary.get(current_user.location).get(couple).get("?")==None):
            voteDictionary.get(current_user.location).get(couple).setdefault("?", 1)
        else:
            idkAmount = voteDictionary.get(current_user.location).get(couple).get("?")
            voteDictionary.get(current_user.location).get(couple).update({"?": idkAmount+1})
        
        #sends necessary data back to front end
        return jsonify(users=sameplace, year1=first, year2=second, score = score, name = current_user.username, satChecker=satChecker, stationChecker=stationChecker, voteChecker=voteChecker, voted=voted)    
    
    #this is in the case the user didn't vote for I Dont Know
    voted=True

    #weather and rainfall variables set up for each year
    weather1 = 0
    weather2 = 0
    rainfall1=0
    rainfall2=0

    #gets current number of votes for year1, year2 and = when comparing only those two years - will create new dictionary for a couple if it hasn't been made yet
    if (voteDictionary.get(current_user.location).get(couple)==None):
        voteDictionary.get(current_user.location).setdefault(couple, dict())
    votes1=voteDictionary.get(current_user.location).get(couple).get(str(first), 0)
    votes2=voteDictionary.get(current_user.location).get(couple).get(str(second), 0)
    votes3=voteDictionary.get(current_user.location).get(couple).get("=", 0)
    votes4=voteDictionary.get(current_user.location).get(couple).get("?", 0)

    #total number of votes increased to be accurate - need this and percent later to send percent of voters agreeing with user
    total=total+votes1+votes2+votes3+votes4
    percent=0

    #gives values to weather and rainfall variables from data in dictionary
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
    
    #if user chooses year1
    if(buttonPressed==1):
        #adds vote to database
        vote = Vote(year1=first, year2=second, answer=str(first), author=current_user)
        db.session.add(vote)
        db.session.commit()

        #if rainfall for year 1 is greater than year 2, increases user score by 50 and sets satellite checker to true, same for weather and station checker
        if(rainfall1>rainfall2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            satChecker=True
        if(weather1>weather2):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            stationChecker=True
        
        #checks that the votes for year 1 when looking at the 2 is higher than votes for year 2 or for equals - if so, user score goes up and vote Checker set to true, percent also calculated
        if(votes1>votes2 and votes1>votes3):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            voteChecker=True
            percent=int(float(votes1)/float(total)*100)
        
        #increases number of votes for that year in that couple in the vote dictionary 
        amount1=voteDictionary.get(current_user.location).get(couple).get(first, 0)
        voteDictionary.get(current_user.location).get(couple).update({first: amount1+1})

        #increases user's score in users list and sorts
        Sortandincrease(sameplace, current_user.id)

        #weather and rainfall set to the first year values so user can see what the value of their answer was
        weather=weather1
        rainfall=rainfall1

    #if user chose year 2 - everything within basically the same function as year 1
    if(buttonPressed==2):
        print (weather1, weather2, rainfall1, rainfall2, votes1, votes2)
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
        if(votes2>votes1 and votes2>votes3):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            voteChecker=True
            percent=int(float(votes2)/float(total)*100)
        amount2=voteDictionary.get(current_user.location).get(couple).get(second, 0)
        voteDictionary.get(current_user.location).get(couple).update({second: amount2})
        db.session.commit()
        Sortandincrease(sameplace, current_user.id)
        weather=weather2
        rainfall=rainfall2
    
    #if user chose equals
    if(buttonPressed==3):
        print (weather1, weather2, rainfall1, rainfall2, votes1, votes2)
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
        if(votes3>votes2 and votes3>votes1):
            u = User.query.get(current_user.id)
            u.increase_score(50)
            voteChecker=True
            percent=int(float(votes3)/float(total)*100)
        equalsAmount=voteDictionary.get(current_user.location).get(couple).get("=", 0)
        voteDictionary.get(current_user.location).get(couple).update({"=": equalsAmount})
        db.session.commit()
        Sortandincrease(sameplace, current_user.id)
        weather=weather1
        rainfall=rainfall1
    
    #sets up new years to ask user
    votes = current_user.votes.all()
    found = True
    while (found):
        found = False
        first = random.randint(2004, 2019)
        second = random.randint(2004, 2019)
        if(first == second):
            if (first==2019):
                second= random.randint(2004, 2018)
            else:
                second=second+1
        for vote in votes:
            if (vote.year1 == first and vote.year2 == second):
                found = True
                break
    score = current_user.score

    #sends necessary data to front end
    return jsonify(users=sameplace, year1=first, year2=second, score = score, name = current_user.username, satChecker=satChecker, stationChecker=stationChecker, voteChecker=voteChecker, voted=voted, weather=weather, rainfall=rainfall, percent=percent)
