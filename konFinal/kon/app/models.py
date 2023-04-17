from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    score = db.Column(db.Integer)
    location = db.Column(db.String(64))
    votes = db.relationship('Vote', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def increase_score(self, number):
        self.score = self.score+number

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year1 = db.Column(db.Integer)
    year2 = db.Column(db.Integer)
    answer = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        response = self.author.username+" voted for "+self.answer+" when asked to vote between "+str(self.year1)+ " and "+ str(self.year2)
        return '<Vote {}>'.format(response)