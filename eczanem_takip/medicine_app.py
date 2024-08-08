import os
import logging
from flask import Blueprint, request, jsonify, render_template
from flask_mysqldb import MySQL
from models.Medicine import Medicine  # Import the Medicine class from your models
import pandas as pd

mysql = MySQL()
logging.basicConfig(filename='/tmp/medicine_processing.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

medicine_bp = Blueprint('medicine', __name__)


@medicine_bp.route('/register_medicine_page', methods=['GET'])
def register_medicine_page():
    return render_template('register_medicine.html')


# Get All Medicines (Read)
@medicine_bp.route('/get_all_medicines', methods=['GET'])
def get_all_medicines():
    try:
        # Get query parameters for pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        # Calculate offset for pagination
        offset = (page - 1) * per_page

        # Retrieve medicines with pagination
        medicines = Medicine.get_all(mysql.connection, limit=per_page, offset=offset)
        total_medicines = Medicine.count_all(mysql.connection)  # Assuming a method to count all medicines

        return jsonify({
            "success": True,
            "medicines": [medicine.serialize() for medicine in medicines],
            "page": page,
            "per_page": per_page,
            "total": total_medicines
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to retrieve medicines", "error": str(e)}), 500


@medicine_bp.route('/search_by_barcode', methods=['GET'])
def search_by_barcode():
    try:
        barcode = request.args.get('barcode', '')
        medicines = Medicine.search_by_barcode(mysql.connection, barcode)
        return jsonify({
            "success": True,
            "medicines": [medicine.serialize() for medicine in medicines]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to search medicines by barcode", "error": str(e)}), 500


@medicine_bp.route('/search_medicines', methods=['GET'])
def search_medicines():
    try:
        # Get query parameters for search and pagination
        name_query = request.args.get('name', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        # Calculate offset for pagination
        offset = (page - 1) * per_page

        # Search medicines with pagination
        medicines = Medicine.search_by_name(mysql.connection, name_query, limit=per_page, offset=offset)
        total_medicines = Medicine.count_by_name(mysql.connection,
                                                 name_query)  # Assuming a method to count search results

        return jsonify({
            "success": True,
            "medicines": [medicine.serialize() for medicine in medicines],
            "page": page,
            "per_page": per_page,
            "total": total_medicines
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to search medicines", "error": str(e)}), 500



# Get Medicine by ID (Read)
@medicine_bp.route('/get_medicine/<int:medicine_id>', methods=['GET'], endpoint='get_medicine')
def get_medicine(medicine_id):
    try:
        medicine = Medicine.get_by_id(mysql.connection, medicine_id)
        if medicine:
            active_ingredients = Medicine.get_active_ingredients_for_medicine(mysql.connection, medicine_id)
            medicine_data = medicine.serialize()
            medicine_data['active_ingredients'] = [ingredient.serialize() for ingredient in active_ingredients]
            return jsonify({"success": True, "medicine": medicine_data}), 200
        else:
            return jsonify({"success": False, "message": "Medicine not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to retrieve medicine", "error": str(e)}), 500


# Update Medicine (Update)
@medicine_bp.route('/update_medicine/<int:medicine_id>', methods=['PUT'], endpoint='update_medicine')
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
    active_ingredients = data.get('active_ingredients', [])  # List of active ingredients

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

        # Update active ingredients
        Medicine.remove_all_active_ingredients(mysql.connection, medicine_id)
        for ingredient in active_ingredients:
            ingredient_name = ingredient.get('name')
            ingredient_amount = ingredient.get('amount')
            if ingredient_name and ingredient_amount:
                active_ingredient_id = Medicine.add_active_ingredient(mysql.connection, ingredient_name,
                                                                      ingredient_amount)
                Medicine.add_medicine_active_ingredient(mysql.connection, medicine_id, active_ingredient_id)

        return jsonify(
            {"success": True, "message": "Medicine successfully updated", "medicine": medicine.serialize()}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to update medicine", "error": str(e)}), 500


# Delete Medicine (Delete)
@medicine_bp.route('/delete_medicine/<int:medicine_id>', methods=['DELETE'], endpoint='delete_medicine')
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


# Register Medicine (Create)
@medicine_bp.route('/register_medicine', methods=['POST'], endpoint='register_medicine')
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
    active_ingredients = data.get('active_ingredients', [])  # List of active ingredients

    if not all([public_number, atc_code, name, brand, barcode]):
        return jsonify(
            {"success": False, "message": "Public number, ATC code, name, brand, and barcode are required"}), 400

    new_medicine = Medicine(None, public_number, atc_code, report_type, name, brand, form, barcode,
                            equivalent_medicine_group)

    try:
        medicine_id = Medicine.add(mysql.connection, new_medicine)
        new_medicine.id = medicine_id

        for ingredient in active_ingredients:
            ingredient_name = ingredient.get('name')
            ingredient_amount = ingredient.get('amount')
            if ingredient_name and ingredient_amount:
                existing_ingredient = Medicine.get_active_ingredient_by_name(mysql.connection, ingredient_name)
                if existing_ingredient:
                    active_ingredient_id = existing_ingredient.id
                else:
                    active_ingredient_id = Medicine.add_active_ingredient(mysql.connection, ingredient_name,
                                                                          ingredient_amount)
                Medicine.add_medicine_active_ingredient(mysql.connection, medicine_id, active_ingredient_id)

        return jsonify({"success": True, "message": "Medicine successfully added to the system.",
                        "medicine": new_medicine.serialize()}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to add medicine", "error": str(e)}), 500
VALID_REPORT_TYPES = {'KIRMIZI', 'MOR', 'TURUNCU', 'YEŞİL', 'NORMAL'}

@medicine_bp.route('/register_medicine_from_excel', methods=['POST'], endpoint='register_medicine_from_excel')
def register_medicine_from_excel():
    # Load the Excel file
    file = request.files['file']
    excel_data = pd.read_excel(file)

    # Replace NaN values with defaults
    excel_data.fillna({
        'Barkod': '',
        'ATC Kodu': '',
        'Reçete Türü': 'NORMAL',
        'İlaç Adı': '',
        'Firma Adı': '',
        'Form': '',
        'Equivalent Medicine Group': '',
        'Active Ingredients': []
    }, inplace=True)

    for index, row in excel_data.iterrows():
        public_number = row['Barkod']
        atc_code = row['ATC Kodu']
        report_type = row['Reçete Türü'].upper()  # Ensure the value is uppercase
        report_type = report_type if report_type in VALID_REPORT_TYPES else 'NORMAL'
        name = row['İlaç Adı'][:200]  # Truncate to match the database column length
        brand = row['Firma Adı'][:200]  # Truncate to match the database column length
        form = row.get('Form', '')[:200]  # Assuming 'Form' column exists in the Excel and truncating
        barcode = row['Barkod']
        equivalent_medicine_group = row.get('Equivalent Medicine Group', '')[:80]  # Assuming column name and truncating
        active_ingredients = row.get('Active Ingredients', [])  # Assuming column name

        if not all([public_number, atc_code, name, brand, barcode]):
            continue  # Skip rows with missing required fields

        new_medicine = Medicine(None, public_number, atc_code, report_type, name, brand, form, barcode,
                                equivalent_medicine_group)

        try:
            medicine_id = Medicine.add(mysql.connection, new_medicine)
            new_medicine.id = medicine_id

            for ingredient in active_ingredients:
                ingredient_name = ingredient.get('name')
                ingredient_amount = ingredient.get('amount')
                if ingredient_name and ingredient_amount:
                    existing_ingredient = Medicine.get_active_ingredient_by_name(mysql.connection, ingredient_name)
                    if existing_ingredient:
                        active_ingredient_id = existing_ingredient.id
                    else:
                        active_ingredient_id = Medicine.add_active_ingredient(mysql.connection, ingredient_name,
                                                                              ingredient_amount)
                    Medicine.add_medicine_active_ingredient(mysql.connection, medicine_id, active_ingredient_id)

        except Exception as e:
            mysql.connection.rollback()
            return jsonify({"success": False, "message": "Failed to add some medicines", "error": str(e)}), 500

    return jsonify({"success": True, "message": "All medicines successfully added to the system."}), 201
# Get Active Ingredient by Name (Read)
@medicine_bp.route('/get_active_ingredient_by_name/<string:name>', methods=['GET'])
def get_active_ingredient_by_name(name):
    try:
        ingredient_name = name.strip().lower()
        ingredient = Medicine.get_active_ingredient_by_name(mysql.connection, ingredient_name)
        if ingredient:
            return jsonify({"success": True, "active_ingredient": ingredient.serialize()}), 200
        else:
            return jsonify({"success": False, "message": "Active ingredient not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to retrieve active ingredient", "error": str(e)}), 500


# Get All Active Ingredients (Read)
@medicine_bp.route('/get_all_active_ingredients', methods=['GET'], endpoint='get_all_active_ingredients')
def get_all_active_ingredients():
    try:
        active_ingredients = Medicine.get_all_active_ingredients(mysql.connection)
        return jsonify(
            {"success": True, "active_ingredients": [ingredient.serialize() for ingredient in active_ingredients]}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to retrieve active ingredients", "error": str(e)}), 500


# Get Active Ingredient by ID (Read)
@medicine_bp.route('/get_active_ingredient/<int:ingredient_id>', methods=['GET'], endpoint='get_active_ingredient')
def get_active_ingredient(ingredient_id):
    try:
        ingredient = Medicine.get_active_ingredient_by_id(mysql.connection, ingredient_id)
        if ingredient:
            return jsonify({"success": True, "active_ingredient": ingredient.serialize()}), 200
        else:
            return jsonify({"success": False, "message": "Active ingredient not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to retrieve active ingredient", "error": str(e)}), 500


@medicine_bp.route('/get_active_ingredients_of_medicine/<int:medicine_id>', methods=['GET'])
def get_active_for_medicine(medicine_id):
    try:
        ingredients = Medicine.get_active_ingredients_for_medicine(mysql.connection, medicine_id)
        if ingredients:
            ing = [ingredient.serialize() for ingredient in ingredients]
            return jsonify({"success": True, "active_ingredients": ing}), 200
        else:
            return jsonify({"success": False, "message": "No active ingredients found for this medicine"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to retrieve active ingredients", "error": str(e)}), 500


# Add Active Ingredient (Create)
@medicine_bp.route('/add_active_ingredient', methods=['POST'], endpoint='add_active_ingredient')
def add_active_ingredient():
    data = request.get_json()
    name = data.get('name')
    amount = data.get('amount')

    if not all([name, amount]):
        return jsonify({"success": False, "message": "Name and amount are required"}), 400

    try:
        ingredient_id = Medicine.add_active_ingredient(mysql.connection, name, amount)
        new_ingredient = Medicine.get_active_ingredient_by_id(mysql.connection, ingredient_id)
        return jsonify({"success": True, "message": "Active ingredient successfully added",
                        "active_ingredient": new_ingredient.serialize()}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to add active ingredient", "error": str(e)}), 500


# Update Active Ingredient (Update)
@medicine_bp.route('/update_active_ingredient/<int:ingredient_id>', methods=['PUT'],
                   endpoint='update_active_ingredient')
def update_active_ingredient(ingredient_id):
    data = request.get_json()
    name = data.get('name')
    amount = data.get('amount')

    try:
        ingredient = Medicine.get_active_ingredient_by_id(mysql.connection, ingredient_id)
        if not ingredient:
            return jsonify({"success": False, "message": "Active ingredient not found"}), 404

        ingredient.name = name
        ingredient.amount = amount

        Medicine.update_active_ingredient(mysql.connection, ingredient)
        return jsonify({"success": True, "message": "Active ingredient successfully updated",
                        "active_ingredient": ingredient.serialize()}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to update active ingredient", "error": str(e)}), 500


# Delete Active Ingredient (Delete)
@medicine_bp.route('/delete_active_ingredient/<int:ingredient_id>', methods=['DELETE'],
                   endpoint='delete_active_ingredient')
def delete_active_ingredient(ingredient_id):
    try:
        ingredient = Medicine.get_active_ingredient_by_id(mysql.connection, ingredient_id)
        if not ingredient:
            return jsonify({"success": False, "message": "Active ingredient not found"}), 404

        Medicine.delete_active_ingredient(mysql.connection, ingredient_id)
        return jsonify({"success": True, "message": "Active ingredient successfully deleted"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to delete active ingredient", "error": str(e)}), 500
