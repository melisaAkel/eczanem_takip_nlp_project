import MySQLdb
from flask import Blueprint, request, jsonify, render_template
from flask_mysqldb import MySQL
from models.Medicine import Medicine

mysql = MySQL()
stock_bp = Blueprint('stock', __name__)
@stock_bp.route('/add_stock', methods=['POST'])
def add_stock():
    data = request.get_json()
    medicine_id = data.get('medicine_id')
    supplier_id = data.get('supplier_id')
    user_id = data.get('user_id')
    expiry_date = data.get('expiry_date')
    quantity = data.get('quantity')

    if not all([medicine_id, supplier_id, user_id, expiry_date, quantity]):
        return jsonify({"success": False, "message": "Medicine ID, Supplier ID, User ID, expiry date, and quantity are required"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO medicine_stock (medicine_id, supplier_id, user_id, expiry_date, quantity)
            VALUES (%s, %s, %s, %s, %s)
        """, (medicine_id, supplier_id, user_id, expiry_date, quantity))
        mysql.connection.commit()
        return jsonify({"success": True, "message": "Stock successfully added"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to add stock", "error": str(e)}), 500
    finally:
        cursor.close()
@stock_bp.route("/buy_stock_page", methods=['GET'])
def buy_stock_page():
    return render_template("buy_stock.html")
# Delete Stock (Delete)
@stock_bp.route('/delete_stock/<int:stock_id>', methods=['DELETE'])
def delete_stock(stock_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM medicine_stock WHERE id = %s", (stock_id,))
        mysql.connection.commit()
        return jsonify({"success": True, "message": "Stock successfully deleted"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to delete stock", "error": str(e)}), 500
    finally:
        cursor.close()

# Update Stock (Update)
@stock_bp.route('/update_stock/<int:stock_id>', methods=['PUT'])
def update_stock(stock_id):
    data = request.get_json()
    quantity = data.get('quantity')
    expiry_date = data.get('expiry_date')

    if not all([quantity, expiry_date]):
        return jsonify({"success": False, "message": "Quantity and expiry date are required"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE medicine_stock
            SET quantity = %s, expiry_date = %s
            WHERE id = %s
        """, (quantity, expiry_date, stock_id))
        mysql.connection.commit()
        return jsonify({"success": True, "message": "Stock successfully updated"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to update stock", "error": str(e)}), 500
    finally:
        cursor.close()

# Get Stock by Medicine ID (Read)
@stock_bp.route('/get_stock_by_medicine/<int:medicine_id>', methods=['GET'])
def get_stock_by_medicine(medicine_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM medicine_stock WHERE medicine_id = %s", (medicine_id,))
        stock_records = cursor.fetchall()
        cursor.close()
        return jsonify({"success": True, "stock": stock_records}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to retrieve stock", "error": str(e)}), 500

@stock_bp.route('/sale_medicine_page')
def sale_medicine_page():
    return render_template('sale_medicine_page.html')

@stock_bp.route('/record_sale', methods=['POST'])
def record_sale():
    data = request.get_json()
    user_id = data.get('user_id')
    medicine_id = data.get('medicine_id')
    customer_name = data.get('customer_name')
    sale_date = data.get('sale_date')
    quantity = data.get('quantity')

    if not all([user_id, medicine_id, sale_date, quantity]):
        return jsonify({"success": False, "message": "User ID, medicine ID, sale date, and quantity are required"}), 400

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check stock
        cursor.execute("""
            SELECT id, quantity FROM medicine_stock
            WHERE medicine_id = %s AND user_id = %s AND quantity > 0
            ORDER BY expiry_date ASC
        """, (medicine_id, user_id))
        stock_records = cursor.fetchall()

        total_available = sum(record['quantity'] for record in stock_records)
        if total_available < quantity:
            return jsonify({"success": False, "message": "Not enough stock to complete the sale"}), 400

        required_quantity = quantity
        for record in stock_records:
            if required_quantity <= 0:
                break

            current_stock_id = record['id']
            current_stock_quantity = record['quantity']

            if current_stock_quantity >= required_quantity:
                # Update the stock with the remaining quantity
                new_quantity = current_stock_quantity - required_quantity
                cursor.execute("""
                    UPDATE medicine_stock
                    SET quantity = %s
                    WHERE id = %s
                """, (new_quantity, current_stock_id))
                required_quantity = 0
            else:
                # Reduce the stock to 0
                cursor.execute("""
                    UPDATE medicine_stock
                    SET quantity = 0
                    WHERE id = %s
                """, (current_stock_id,))
                required_quantity -= current_stock_quantity

        # Record sale
        cursor.execute("""
            INSERT INTO medicine_sales (user_id, medicine_id, customer_name, sale_date, quantity)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, medicine_id, customer_name, sale_date, quantity))

        mysql.connection.commit()
        return jsonify({"success": True, "message": "Sale successfully recorded"}), 201

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Failed to record sale", "error": str(e)}), 500

    finally:
        cursor.close()



@stock_bp.route("/view_stock_page", methods=['GET'])
def view_stock_page():
    return render_template("view_stock.html")


@stock_bp.route('/filter_stock', methods=['GET'])
def filter_stock():
    user_id = request.args.get('user_id')
    supplier_name = request.args.get('supplier_name')
    medicine_name = request.args.get('medicine_name')
    barcode = request.args.get('barcode')
    expiry_date = request.args.get('expiry_date')
    page = int(request.args.get('page', 1))  # Default to page 1
    per_page = int(request.args.get('per_page', 10))  # Default to 10 items per page

    offset = (page - 1) * per_page

    query = """
        SELECT ms.*, m.name AS medicine_name, m.barcode AS medicine_barcode, s.name AS supplier_name
        FROM medicine_stock ms
        JOIN medicine m ON ms.medicine_id = m.id
        JOIN supplier s ON ms.supplier_id = s.id
        WHERE ms.user_id = %s
    """
    query_params = [user_id]

    if supplier_name:
        query += " AND s.name LIKE %s"
        query_params.append(f"%{supplier_name}%")

    if medicine_name:
        query += " AND m.name LIKE %s"
        query_params.append(f"%{medicine_name}%")

    if barcode:
        query += " AND m.barcode = %s"
        query_params.append(barcode)

    if expiry_date:
        query += " AND ms.expiry_date <= %s"
        query_params.append(expiry_date)

    query += " ORDER BY m.name ASC LIMIT %s OFFSET %s"
    query_params.extend([per_page, offset])

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query, query_params)
        filtered_stocks = cursor.fetchall()

        # Count total items for pagination
        count_query = """
            SELECT COUNT(*) as total
            FROM medicine_stock ms
            JOIN medicine m ON ms.medicine_id = m.id
            JOIN supplier s ON ms.supplier_id = s.id
            WHERE ms.user_id = %s
        """
        count_query_params = [user_id]

        if supplier_name:
            count_query += " AND s.name LIKE %s"
            count_query_params.append(f"%{supplier_name}%")

        if medicine_name:
            count_query += " AND m.name LIKE %s"
            count_query_params.append(f"%{medicine_name}%")

        if barcode:
            count_query += " AND m.barcode = %s"
            count_query_params.append(barcode)

        if expiry_date:
            count_query += " AND ms.expiry_date <= %s"
            count_query_params.append(expiry_date)

        cursor.execute(count_query, count_query_params)
        total_items = cursor.fetchone()['total']
        cursor.close()

        total_pages = (total_items + per_page - 1) // per_page  # Calculate total pages

        return jsonify({
            "success": True,
            "stocks": filtered_stocks,
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_items": total_items,
                "total_pages": total_pages
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Failed to filter stocks", "error": str(e)}), 500
