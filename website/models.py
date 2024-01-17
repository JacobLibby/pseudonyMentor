from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    type_of_user = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    callsign = db.Column(db.String(300))


class Mentor(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    major = db.Column(db.String(200), nullable=True)
    grad_year = db.Column(db.Integer, nullable=True)
    bio = db.Column(db.String(300), nullable=True)
    position = db.Column(db.String(200), nullable=True)
    levelOfEducation = db.Column(db.String(100), nullable=True)
    verified = db.Column(db.Boolean, default=False)

class Mentee(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    major = db.Column(db.String(200), nullable=True)
    grad_year = db.Column(db.Integer, nullable=True)
    bio = db.Column(db.String(300), nullable=True)
    current_school = db.Column(db.String(200), nullable=True)
    verified = db.Column(db.Boolean, default=False)

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    levelOfAccess = db.Column(db.Integer)

# class School(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(200))
#     location = db.Column(db.String(200))

# class Company(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(200))
#     location = db.Column(db.String(200))    

class Connections(db.Model):
    mentorID = db.Column(db.Integer, primary_key=True)
    menteeID = db.Column(db.Integer, primary_key=True)
    id_sentBy = db.Column(db.Integer)
    date_sent = db.Column(db.DateTime)
    date_accepted = db.Column(db.DateTime, nullable=True)

