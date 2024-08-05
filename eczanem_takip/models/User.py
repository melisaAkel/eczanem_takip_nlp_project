from . import db
from sqlalchemy.orm import relationship
from .Medicine import user_medicine  # Import the association table

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    mail = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    medicines = relationship('Medicine', secondary=user_medicine, back_populates='users')
