from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import PickleType
from Tool import db, login_manager

# Association table for many-to-many relationship between users and clubs (for club requesters)
requesters = db.Table('requesters',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'))
)

# Association table for many-to-many relationship between users and forums (for participants)
participants_forums = db.Table('participants_forums',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('forum_id', db.Integer, db.ForeignKey('forum.id'))
)

# Association table for many-to-many relationship for club managers
managers = db.Table('managers',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'))
)

# Association table for many-to-many relationship for club members
club_members = db.Table('club_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'))
)




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# User model
class User(db.Model, UserMixin):
    __tablename__ = 'user'  # Table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    golds = db.Column(db.Integer, default=0)
    silvers = db.Column(db.Integer, default=0)
    bronzes = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    
    # Define relationships with specific foreign keys
    events_first_place = db.relationship('Event', foreign_keys='Event.first_place', backref='user_first_place')
    events_second_place = db.relationship('Event', foreign_keys='Event.second_place', backref='user_second_place')
    events_third_place = db.relationship('Event', foreign_keys='Event.third_place', backref='user_third_place')

    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_pic = db.Column(db.String(200), nullable=True)
    notifications = db.Column(PickleType, default=[])  # List of notifications as strings

    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    
    # Use back_populates to explicitly define relationships
    clubs = db.relationship('Club', secondary=club_members, back_populates='members')

    # Many-to-many relationship for clubs a user manages
    managed_club = db.relationship('Club', secondary='managers', back_populates='managers')

    # Many-to-many relationship for requested clubs
    requested_clubs = db.relationship('Club', secondary=requesters, back_populates='requesters')

    def __init__(self, name, email, password, golds=0, silvers=0, bronzes=0, club_id=None):
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)  # Hashing the password
        self.golds = golds
        self.silvers = silvers
        self.bronzes = bronzes
        self.total = golds + silvers + bronzes
        self.club_id = club_id
        self.notifications = []  # Initialize empty list for notifications

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  # Checking password hash

    def add_notification(self, message):
        """Adds a new notification to the user's list of notifications."""
        self.notifications.append(message)
        db.session.commit()

    def clear_notifications(self):
        """Clears all notifications for the user."""
        self.notifications = []
        db.session.commit()

    def __repr__(self):
        return f'<User {self.name}-{self.id}>'

# Club model
class Club(db.Model):
    __tablename__ = 'club'  # Table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    events_pcpts = db.relationship('Event', backref='host_club')
    golds = db.Column(db.Integer, default=0)
    silvers = db.Column(db.Integer, default=0)
    bronzes = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    members = db.relationship('User', secondary=club_members, back_populates='clubs')
    managers = db.relationship('User', secondary='managers', back_populates='managed_club')
    requesters = db.relationship('User', secondary=requesters, back_populates='requested_clubs')

    def __repr__(self):
        return f'<Club {self.name}-{self.id}>'

# Event model
class Event(db.Model):
    __tablename__ = 'event'  # Table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    host_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    first_place = db.Column(db.Integer, db.ForeignKey('user.id'))
    second_place = db.Column(db.Integer, db.ForeignKey('user.id'))
    third_place = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Event {self.name}>'

# Forum model
class Forum(db.Model):
    __tablename__ = 'forum'  # Table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    comments = db.relationship('Comment', backref='forum', lazy=True)
    members = db.relationship('User', secondary=participants_forums, backref='forums')

    def __repr__(self):
        return f'<Forum {self.name}>'

# Comment model
class Comment(db.Model):
    __tablename__ = 'comment'  # Table name
    id = db.Column(db.Integer, primary_key=True)
    forum_id = db.Column(db.Integer, db.ForeignKey('forum.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Comment {self.content} by User {self.user_id} on Forum {self.forum_id}>'
