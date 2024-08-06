from flask import Blueprint, request, jsonify

medicine_bp = Blueprint('medicine', __name__)
from flask_mysqldb import MySQL
from models.Medicine import Medicine

mysql = MySQL()


@medicine_bp.route('/register_medicine', methods=['POST'])
def register_medicine():
    data = request.get_json()
    public_number = data.get('public_number')
    name = data.get('name')
    brand = data.get('brand')
    form = data.get('form')
    barcode = data.get('barcode')
    equivalent_medicine_group = data.get('equivalent_medicine_group')

    if not all([public_number, name, brand, barcode]):
        return jsonify({"success": False, "message": "Public number, name, brand, and barcode are required"}), 400

    new_medicine = Medicine(None, public_number, name, brand, form, barcode, equivalent_medicine_group)

    try:
        Medicine.add(mysql.connection, new_medicine)
        return jsonify({"success": True, "message": "Medicine successfully added to the system.",
                        "medicine": new_medicine.serialize()}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to add medicine", "error": str(e)}), 500
