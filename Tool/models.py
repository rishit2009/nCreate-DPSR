from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import PickleType
from Tool import db, login_manager

# Association tables for many-to-many relationships

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

# New association table for many-to-many relationship between clubs and events (participating clubs)
event_clubs = db.Table('event_clubs',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'))
)

# New association table for many-to-many relationship between users and events (individual participants)
event_users = db.Table('event_users',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)


sub_event_registrations = db.Table('sub_event_registrations',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('sub_event_id', db.Integer, db.ForeignKey('sub_event.id'))
)


sub_event_club_registrations = db.Table('sub_event_club_registrations',
    db.Column('club_id', db.Integer, db.ForeignKey('club.id')),
    db.Column('sub_event_id', db.Integer, db.ForeignKey('sub_event.id'))
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# User model
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    golds = db.Column(db.Integer, default=0)
    silvers = db.Column(db.Integer, default=0)
    bronzes = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    
    
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    notifications = db.Column(PickleType, default=[])  # List of notifications as strings

    # One-to-many relationship: a user can be part of only one club
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))

    # Many-to-many relationship for clubs a user manages
    managed_club = db.relationship('Club', secondary='managers', back_populates='managers')

    # Many-to-many relationship for requested clubs
    requested_clubs = db.relationship('Club', secondary=requesters, back_populates='requesters')

    # Many-to-many relationship for events the user participates in
    events = db.relationship('Event', secondary=event_users, back_populates='participants')


    registered_sub_events = db.relationship('SubEvent', secondary=sub_event_registrations, back_populates='registered_users')


    profile_pic = db.Column(db.String(200), nullable=False)

    description = db.Column(db.String, nullable = False)

    def __init__(self, name, email, password,profile_pic = '/Tool/static/images/default.jpg', golds=0, silvers=0, bronzes=0, club_id=1):
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)  # Hashing the password
        self.golds = golds
        self.silvers = silvers
        self.bronzes = bronzes
        self.total = golds + silvers + bronzes
        self.club_id = club_id
        self.profile_pic = profile_pic
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
        return f'<User {self.name}-{self.id} in club {self.club_id}>'

# Club model
class Club(db.Model):
    __tablename__ = 'club'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    golds = db.Column(db.Integer, default=0)
    silvers = db.Column(db.Integer, default=0)
    bronzes = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)


    # One-to-many relationship: a club can have many users, but a user can belong to only one club
    members = db.relationship('User', backref='club')

    managers = db.relationship('User', secondary='managers', back_populates='managed_club')
    requesters = db.relationship('User', secondary=requesters, back_populates='requested_clubs')

    # Many-to-many relationship for clubs participating in events
    events = db.relationship('Event', secondary=event_clubs, back_populates='clubs')

    submissions = db.relationship('Submission', back_populates='club')


    registered_sub_events = db.relationship('SubEvent', secondary=sub_event_club_registrations, back_populates='registered_clubs')


    profile_pic = db.Column(db.String(200), nullable=False, default = '/Tool/static/images/default.jpg')

    description = db.Column(db.String, nullable = False)


    def __repr__(self):
        return f'<Club {self.name}-{self.id}>'

# Event model
class Event(db.Model):
    __tablename__ = 'event'  # Table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    host_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)

     #all 5 should be nullable = false, are true for testing purposes
    registration_end_date = db.Column(db.DateTime, nullable=True) 
    prompts_date = db.Column(db.DateTime, nullable=True)  
    submission_date = db.Column(db.DateTime, nullable=True)  
    event_date = db.Column(db.DateTime, nullable=True)
    result_date = db.Column(db.DateTime, nullable=True)

    brochure_link = db.Column(db.String(255), nullable=True)

    clubs = db.relationship('Club', secondary=event_clubs, back_populates='events')

    participants = db.relationship('User', secondary=event_users, back_populates='events')

    sub_events = db.relationship('SubEvent', backref='parent_event', cascade='all, delete-orphan', lazy=True)

    profile_pic = db.Column(db.String(200), nullable=False, default = '/Tool/static/images/default.jpg')

    description = db.Column(db.String, nullable = False)
    
    def __repr__(self):
        return f'<Event {self.name}>'
    

class SubEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    participant_count = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable = False)
    registered_users = db.relationship('User', secondary=sub_event_registrations, back_populates='registered_sub_events')
    submissions = db.relationship('Submission', back_populates='sub_event')
    registered_clubs = db.relationship('Club', secondary=sub_event_club_registrations, back_populates='registered_sub_events')

    # Foreign keys for 1st, 2nd, and 3rd place clubs
    first_place_club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=True)
    second_place_club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=True)
    third_place_club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=True)

    # Relationships to access club data with new backrefs
    first_place_club = db.relationship('Club', foreign_keys=[first_place_club_id], backref='won_first_place_sub_events')
    second_place_club = db.relationship('Club', foreign_keys=[second_place_club_id], backref='won_second_place_sub_events')
    third_place_club = db.relationship('Club', foreign_keys=[third_place_club_id], backref='won_third_place_sub_events')



# Submission model: linking clubs, sub-events, and submission links
class Submission(db.Model):
    __tablename__ = 'submission'
    id = db.Column(db.Integer, primary_key=True)
    
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    club = db.relationship('Club', back_populates='submissions')

    sub_event_id = db.Column(db.Integer, db.ForeignKey('sub_event.id'), nullable=False)
    sub_event = db.relationship('SubEvent', back_populates='submissions')

    submission_link = db.Column(db.String(255), nullable=False)

    submission_date = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f'<Submission from Club {self.club_id} for SubEvent {self.sub_event_id}>'

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
