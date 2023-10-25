from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
import os

class ClubMembership(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), primary_key=True)
    # Add additional attributes if needed
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # Define the many-to-many relationship between users and clubs.
    clubs = db.relationship('Club', secondary=ClubMembership.__table__, back_populates='members')
    
    # Define the one-to-one relationship for the club ownership.
    owned_club = db.relationship('Club', uselist=False, back_populates='owner')

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_member(self, club):
        return club in self.clubs
    


class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # Define the many-to-many relationship between clubs and users.
    members = db.relationship('User', secondary=ClubMembership.__table__, back_populates='clubs')

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', back_populates='owned_club')

    def __repr__(self):
        return '<Club {}>'.format(self.name)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

CLIENT_ID = os.environ.get('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.environ.get('STRAVA_CLIENT_SECRET')

class StravaUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strava_id = db.Column(db.Integer)
    username = db.Column(db.String(30))
    token = db.Column(db.String(40))
    refresh_token = db.Column(db.String(40))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<StravaUser {}>'.format(self.username)
    
@login.user_loader
def load_user(id):
    return StravaUser.query.get(int(id))