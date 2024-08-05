from . import db
from sqlalchemy.orm import relationship
from .User import User  # Import the User model for relationship

# Association table for many-to-many relationship between User and Medicine
user_medicine = db.Table('user_medicine',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('medicine_id', db.Integer, db.ForeignKey('medicine.id'), primary_key=True)
)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_number = db.Column(db.String(80), nullable=False)  # Added publicNumber
    name = db.Column(db.String(80), nullable=False)
    brand = db.Column(db.String(80), nullable=False)
    form = db.Column(db.String(80), nullable=True)
    reorder_level = db.Column(db.Integer, nullable=False)
    barcode = db.Column(db.String(80), nullable=False)
    equivalent_medicine_group = db.Column(db.String(80), nullable=True)  # Added equivalent_medicine_group
    active_ingredients = relationship('ActiveIngredient', backref='medicine', lazy=True)
    stocks = relationship('MedicineStock', backref='medicine', lazy=True)
    users = relationship('User', secondary=user_medicine, back_populates='medicines')

class ActiveIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.String(80), nullable=False)  # e.g., '500mg'
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    contact_info = db.Column(db.String(255))

class MedicineStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    storage_conditions = db.Column(db.String(255), nullable=True)
    __table_args__ = (db.UniqueConstraint('medicine_id', 'supplier_id', 'expiry_date', name='unique_medicine_supplier_expiry'),)
