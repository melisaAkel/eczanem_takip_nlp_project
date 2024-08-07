import MySQLdb
from flask import Blueprint, request, jsonify
from flask_mysqldb import MySQL

mysql = MySQL()
supplier_bp = Blueprint('supplier', __name__)


# Add Supplier (Create)
@supplier_bp.route('/add_supplier', methods=['POST'])
def add_supplier():
    data = request.get_json()
    name = data.get('name')
    contact_info = data.get('contact_info')

    if not name:
        return jsonify({"success": False, "message": "Name is required"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO supplier (name, contact_info)
            VALUES (%s, %s)
        """, (name, contact_info))
        mysql.connection.commit()
        return jsonify({"success": True, "message": "Supplier successfully added"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to add supplier", "error": str(e)}), 500
    finally:
        cursor.close()


# Get All Suppliers (Read)
@supplier_bp.route('/get_all_suppliers', methods=['GET'])
def get_all_suppliers():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM supplier")
        suppliers = cursor.fetchall()
        cursor.close()
        return jsonify({"success": True, "suppliers": suppliers}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to retrieve suppliers", "error": str(e)}), 500


# Get Supplier by ID (Read)
@supplier_bp.route('/get_supplier/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM supplier WHERE id = %s", (supplier_id,))
        supplier = cursor.fetchone()
        cursor.close()
        if supplier:
            return jsonify({"success": True, "supplier": supplier}), 200
        else:
            return jsonify({"success": False, "message": "Supplier not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to retrieve supplier", "error": str(e)}), 500


# Update Supplier (Update)
@supplier_bp.route('/update_supplier/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    data = request.get_json()
    name = data.get('name')
    contact_info = data.get('contact_info')

    if not name:
        return jsonify({"success": False, "message": "Name is required"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE supplier
            SET name = %s, contact_info = %s
            WHERE id = %s
        """, (name, contact_info, supplier_id))
        mysql.connection.commit()
        return jsonify({"success": True, "message": "Supplier successfully updated"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to update supplier", "error": str(e)}), 500
    finally:
        cursor.close()


# Delete Supplier (Delete)
@supplier_bp.route('/delete_supplier/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM supplier WHERE id = %s", (supplier_id,))
        mysql.connection.commit()
        return jsonify({"success": True, "message": "Supplier successfully deleted"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to delete supplier", "error": str(e)}), 500
    finally:
        cursor.close()
