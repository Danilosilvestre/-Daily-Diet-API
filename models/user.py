from database import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    # Id(Int) username(Str), Email(Str), Password(Str), role(Str)
    id = db.Column(db.Integer, primary_key=True )
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(80), default='user', nullable=False)

    meals = db.relationship('Meal', backref='user', lazy=True)