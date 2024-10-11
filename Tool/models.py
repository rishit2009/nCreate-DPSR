from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from Tool import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

Base = db.Model

# Correct the table names in ForeignKey references
user_club = Table(
    'user_club', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),  # Referencing 'users' table
    Column('club_id', Integer, ForeignKey('clubs.id'))   # Referencing 'clubs' table
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    club = Column(Integer, nullable=True)
    golds = Column(Integer, default=0)
    silvers = Column(Integer, default=0)
    bronzes = Column(Integer, default=0)
    total = Column(Integer, default=0)
    password_hash = Column(String)
    email = Column(String, unique=True)

    user_clubs = relationship('Club', secondary='user_club', back_populates='members')

    def __init__(self, name, email, password, golds=0, silvers=0, bronzes=0, club=None):
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)  # Hash the password
        self.golds = golds
        self.silvers = silvers
        self.bronzes = bronzes
        self.total = golds + silvers + bronzes  # Compute the total medals
        self.club = club

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Club(Base):
    __tablename__ = 'clubs'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    golds = Column(Integer, default=0)
    silvers = Column(Integer, default=0)
    bronzes = Column(Integer, default=0)
    total = Column(Integer, default=0)

    # Relationship to users
    members = relationship('User', secondary='user_club', back_populates='user_clubs')
