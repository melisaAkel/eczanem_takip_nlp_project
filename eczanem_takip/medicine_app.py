from flask import Blueprint, request, jsonify
from models import db
from models.Medicine import Medicine, ActiveIngredient, Supplier, MedicineStock

medicine_bp = Blueprint('medicine', __name__)


# Create a new medicine
@medicine_bp.route('/medicines', methods=['POST'])
def create_medicine():
    data = request.get_json()
    new_medicine = Medicine(
        public_number=data.get('public_number'),
        name=data.get('name'),
        brand=data.get('brand'),
        form=data.get('form'),
        reorder_level=data.get('reorder_level'),
        barcode=data.get('barcode'),
        equivalent_medicine_group=data.get('equivalent_medicine_group')
    )
    db.session.add(new_medicine)
    db.session.commit()
    return jsonify({'message': 'Medicine created successfully'}), 201


# Get all medicines
@medicine_bp.route('/medicines', methods=['GET'])
def get_medicines():
    medicines = Medicine.query.all()
    return jsonify([medicine.serialize() for medicine in medicines])


# Get a single medicine
@medicine_bp.route('/medicines/<int:id>', methods=['GET'])
def get_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    return jsonify(medicine.serialize())


# Update a medicine
@medicine_bp.route('/medicines/<int:id>', methods=['PUT'])
def update_medicine(id):
    data = request.get_json()
    medicine = Medicine.query.get_or_404(id)
    medicine.public_number = data.get('public_number')
    medicine.name = data.get('name')
    medicine.brand = data.get('brand')
    medicine.form = data.get('form')
    medicine.reorder_level = data.get('reorder_level')
    medicine.barcode = data.get('barcode')
    medicine.equivalent_medicine_group = data.get('equivalent_medicine_group')
    db.session.commit()
    return jsonify({'message': 'Medicine updated successfully'})


# Delete a medicine
@medicine_bp.route('/medicines/<int:id>', methods=['DELETE'])
def delete_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    db.session.delete(medicine)
    db.session.commit()
    return jsonify({'message': 'Medicine deleted successfully'})


