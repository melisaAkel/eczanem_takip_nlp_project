import os
import logging
from flask import Blueprint, request, jsonify
from flask_mysqldb import MySQL
from models.Medicine import Medicine  # Import the Medicine class from your models
import pandas as pd
mysql = MySQL()
logging.basicConfig(filename='/tmp/medicine_processing.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

medicine_bp = Blueprint('medicine', __name__)

# Register Medicine (Create)
@medicine_bp.route('/register_medicine', methods=['POST'])
def register_medicine():
    data = request.get_json()
    public_number = data.get('public_number')
    atc_code = data.get('atc_code')
    report_type = data.get('report_type', 'NORMAL')
    name = data.get('name')
    brand = data.get('brand')
    form = data.get('form')
    barcode = data.get('barcode')
    equivalent_medicine_group = data.get('equivalent_medicine_group')

    if not all([public_number, atc_code, name, brand, barcode]):
        return jsonify({"success": False, "message": "Public number, ATC code, name, brand, and barcode are required"}), 400

    new_medicine = Medicine(None, public_number, atc_code, report_type, name, brand, form, barcode, equivalent_medicine_group)

    try:
        medicine_id = Medicine.add(mysql.connection, new_medicine)
        new_medicine.id = medicine_id
        return jsonify({"success": True, "message": "Medicine successfully added to the system.",
                        "medicine": new_medicine.serialize()}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to add medicine", "error": str(e)}), 500

# Get All Medicines (Read)
@medicine_bp.route('/get_all_medicines', methods=['GET'])
def get_all_medicines():
    try:
        medicines = Medicine.get_all(mysql.connection)
        return jsonify({"success": True, "medicines": [medicine.serialize() for medicine in medicines]}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to retrieve medicines", "error": str(e)}), 500

# Get Medicine by ID (Read)
@medicine_bp.route('/get_medicine/<int:medicine_id>', methods=['GET'])
def get_medicine(medicine_id):
    try:
        medicine = Medicine.get_by_id(mysql.connection, medicine_id)
        if medicine:
            return jsonify({"success": True, "medicine": medicine.serialize()}), 200
        else:
            return jsonify({"success": False, "message": "Medicine not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to retrieve medicine", "error": str(e)}), 500

# Update Medicine (Update)
@medicine_bp.route('/update_medicine/<int:medicine_id>', methods=['PUT'])
def update_medicine(medicine_id):
    data = request.get_json()
    public_number = data.get('public_number')
    atc_code = data.get('atc_code')
    report_type = data.get('report_type')
    name = data.get('name')
    brand = data.get('brand')
    form = data.get('form')
    barcode = data.get('barcode')
    equivalent_medicine_group = data.get('equivalent_medicine_group')

    try:
        medicine = Medicine.get_by_id(mysql.connection, medicine_id)
        if not medicine:
            return jsonify({"success": False, "message": "Medicine not found"}), 404

        medicine.public_number = public_number
        medicine.atc_code = atc_code
        medicine.report_type = report_type
        medicine.name = name
        medicine.brand = brand
        medicine.form = form
        medicine.barcode = barcode
        medicine.equivalent_medicine_group = equivalent_medicine_group

        Medicine.update(mysql.connection, medicine)
        return jsonify({"success": True, "message": "Medicine successfully updated", "medicine": medicine.serialize()}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to update medicine", "error": str(e)}), 500

# Delete Medicine (Delete)
@medicine_bp.route('/delete_medicine/<int:medicine_id>', methods=['DELETE'])
def delete_medicine(medicine_id):
    try:
        medicine = Medicine.get_by_id(mysql.connection, medicine_id)
        if not medicine:
            return jsonify({"success": False, "message": "Medicine not found"}), 404

        Medicine.delete(mysql.connection, medicine_id)
        return jsonify({"success": True, "message": "Medicine successfully deleted"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to delete medicine", "error": str(e)}), 500

# Record Sale by Name or Barcode (Create)
@medicine_bp.route('/record_sale', methods=['POST'])
def record_sale():
    data = request.get_json()
    user_id = data.get('user_id')
    identifier = data.get('identifier')  # Can be name or barcode
    customer_name = data.get('customer_name')
    sale_date = data.get('sale_date')
    quantity = data.get('quantity')

    if not all([user_id, identifier, sale_date, quantity]):
        return jsonify({"success": False, "message": "User ID, identifier, sale date, and quantity are required"}), 400

    try:
        Medicine.record_sale_by_name_or_barcode(mysql.connection, user_id, identifier, customer_name, sale_date, quantity)
        return jsonify({"success": True, "message": "Sale successfully recorded"}), 201
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to record sale", "error": str(e)}), 500



def process_excel_file(file_path):
    try:
        # Read the Excel file with the correct header row
        df = pd.read_excel(file_path, skiprows=2, nrows=100)

        # Log the entire DataFrame for debugging
        logging.debug(f"DataFrame head:\n{df.head()}")

        # Log original column names for debugging
        original_columns = df.columns.tolist()
        logging.debug(f"Original column names: {original_columns}")

        # Strip and lower case the column names
        df.columns = df.columns.str.strip().str.lower()

        # Log stripped and lower cased column names for debugging
        stripped_columns = df.columns.tolist()
        logging.debug(f"Stripped and lower cased column names: {stripped_columns}")

        # Log each column name and its length for detailed inspection
        for col in df.columns:
            logging.debug(f"Column: '{col}' Length: {len(col)}")

        medicines = []
        for _, row in df.iterrows():
            logging.debug(f"Row data: {row}")  # Log each row for debugging
            medicine = Medicine(
                id=None,
                public_number=None,  # Adjust if there's a column for this, use row['column_name']
                atc_code=row['atc kodu'].strip(),  # Ensure no leading/trailing spaces
                report_type=row['reçete türü'].strip(),
                name=row['ilaç adı'].strip(),
                brand=row['firma adı'].strip(),
                form=None,  # Adjust if there's a column for this, use row['column_name']
                barcode=row['barkod'].strip(),
                equivalent_medicine_group=None  # Adjust if there's a column for this, use row['column_name']
            )
            medicines.append(medicine)
        return medicines
    except KeyError as e:
        logging.error(f"Column not found: {e}")  # Log the missing column for debugging
        raise e
    except Exception as e:
        logging.error(f"Error processing file: {e}")  # Log the error for debugging
        raise e

@medicine_bp.route('/upload_excel', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400
    if file and file.filename.endswith('.xlsx'):
        file_path = os.path.join('/tmp', file.filename)
        file.save(file_path)
        try:
            medicines = process_excel_file(file_path)
            for medicine in medicines:
                medicine_id = Medicine.add(mysql.connection, medicine)
                medicine.id = medicine_id
            return jsonify({"success": True, "message": "Medicines successfully added to the system."}), 201
        except KeyError as e:
            return jsonify({"success": False, "message": f"Missing column: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"success": False, "message": "Failed to process file", "error": str(e)}), 500
    else:
        return jsonify({"success": False, "message": "Unsupported file format"}), 400