from . import db

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_number = db.Column(db.String(80), nullable=False)  # Added publicNumber
    name = db.Column(db.String(80), nullable=False)
    brand = db.Column(db.String(80), nullable=False)
    form = db.Column(db.String(80), nullable=True)
    reorder_level = db.Column(db.Integer, nullable=False)
    barcode = db.Column(db.String(80), nullable=False)
    equivalent_medicine_group = db.Column(db.String(80), nullable=True)  # Added equivalent_medicine_group
    active_ingredients = db.relationship('ActiveIngredient', backref='medicine', lazy=True)
    stocks = db.relationship('MedicineStock', backref='medicine', lazy=True)

    def serialize(self):
        return {
            'id': self.id,
            'public_number': self.public_number,
            'name': self.name,
            'brand': self.brand,
            'form': self.form,
            'reorder_level': self.reorder_level,
            'barcode': self.barcode,
            'equivalent_medicine_group': self.equivalent_medicine_group
        }

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
