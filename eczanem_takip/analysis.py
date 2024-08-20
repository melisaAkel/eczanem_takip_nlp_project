import pandas as pd
import MySQLdb
from flask import Blueprint, jsonify, request, render_template
from flask_mysqldb import MySQL

mysql = MySQL()
analysis_bp = Blueprint('analysis', __name__)


from flask import jsonify
import MySQLdb.cursors

@analysis_bp.route('/for_sale_analysis/<int:medicine_id>', methods=['POST'])
def for_sale_analysis(medicine_id):
    try:
        # Open database connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query 1: Total Sales in the Last Month
        query_total_sales_last_month = """
            SELECT 
                SUM(quantity) AS total_sales_last_month
            FROM 
                medicine_sales
            WHERE 
                medicine_id = %s
                AND sale_date >= CURDATE() - INTERVAL 1 MONTH;
        """
        cursor.execute(query_total_sales_last_month, (medicine_id,))
        total_sales_last_month = cursor.fetchone()['total_sales_last_month']

        # Query 2: Average Monthly Sales in the Last Year
        query_avg_monthly_sales_last_year = """
            SELECT 
                AVG(monthly_sales) AS average_monthly_sales_last_year
            FROM (
                SELECT 
                    DATE_FORMAT(sale_date, '%%Y-%%m') AS month,
                    SUM(quantity) AS monthly_sales
                FROM 
                    medicine_sales
                WHERE 
                    medicine_id = %s
                    AND sale_date >= CURDATE() - INTERVAL 1 YEAR
                GROUP BY 
                    DATE_FORMAT(sale_date, '%%Y-%%m')
            ) AS monthly_sales_data;
        """
        cursor.execute(query_avg_monthly_sales_last_year, (medicine_id,))
        avg_monthly_sales_last_year = cursor.fetchone()['average_monthly_sales_last_year']

        # Query 3: Total Sales in the Last 3 Months
        query_total_sales_last_three_months = """
            SELECT 
                SUM(quantity) AS total_sales_last_three_months
            FROM 
                medicine_sales
            WHERE 
                medicine_id = %s
                AND sale_date >= CURDATE() - INTERVAL 3 MONTH;
        """
        cursor.execute(query_total_sales_last_three_months, (medicine_id,))
        total_sales_last_three_months = cursor.fetchone()['total_sales_last_three_months']

        # Query 4: Average Sales in the Last 6 Months
        query_avg_sales_last_six_months = """
            SELECT 
                AVG(monthly_sales) AS average_sales_last_six_months
            FROM (
                SELECT 
                    DATE_FORMAT(sale_date, '%%Y-%%m') AS month,
                    SUM(quantity) AS monthly_sales
                FROM 
                    medicine_sales
                WHERE 
                    medicine_id = %s
                    AND sale_date >= CURDATE() - INTERVAL 6 MONTH
                GROUP BY 
                    DATE_FORMAT(sale_date, '%%Y-%%m')
            ) AS six_months_sales_data;
        """
        cursor.execute(query_avg_sales_last_six_months, (medicine_id,))
        avg_sales_last_six_months = cursor.fetchone()['average_sales_last_six_months']

        # Close cursor
        cursor.close()

        # Handle Decimal type (if necessary, convert to float)
        total_sales_last_month = float(total_sales_last_month or 0)
        avg_monthly_sales_last_year = float(avg_monthly_sales_last_year or 0)
        total_sales_last_three_months = float(total_sales_last_three_months or 0)
        avg_sales_last_six_months = float(avg_sales_last_six_months or 0)

        # Prepare the JSON response
        response = {
            "success": True,
            "medicine_id": medicine_id,
            "total_sales_last_month": total_sales_last_month,
            "average_monthly_sales_last_year": avg_monthly_sales_last_year,
            "total_sales_last_three_months": total_sales_last_three_months,
            "average_sales_last_six_months": avg_sales_last_six_months
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Failed to fetch sales analysis", "error": str(e)}), 500

@analysis_bp.route('/total_sales_by_medicine', methods=['POST'])
def total_sales_by_medicine():
    user_id = request.json.get('user_id')
    start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')

    if not user_id:
        return jsonify({"success": False, "message": "User ID is required"}), 400

    query_base = """
        SELECT ms.medicine_id, SUM(ms.quantity) AS total_quantity, m.name AS medicine_name, m.barcode
        FROM medicine_sales ms
        JOIN medicine m ON ms.medicine_id = m.id
        WHERE ms.user_id = %s
    """
    query_params = [user_id]

    if start_date and end_date:
        query_base += " AND ms.sale_date BETWEEN %s AND %s"
        query_params.extend([start_date, end_date])

    query_base += " GROUP BY ms.medicine_id, m.name, m.barcode"

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query_base, query_params)
        sales_data = cursor.fetchall()
        cursor.close()

        if not sales_data:
            return jsonify({"success": False, "message": "No sales data found"}), 404

        # Convert data to a serializable format
        sales_summary = [
            {
                "medicine_id": row["medicine_id"],
                "medicine_name": row["medicine_name"],
                "barcode": row["barcode"],
                "total_quantity": int(row["total_quantity"])
            }
            for row in sales_data
        ]

        return jsonify({"success": True, "sales_summary": sales_summary}), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Failed to calculate total sales", "error": str(e)}), 500


@analysis_bp.route('/top_medicines', methods=['POST'])
def top_medicines():
    try:
        # Get data from the request
        x = request.json.get('x')  # Number of top medicines to return
        months = request.json.get('months')  # Period in months (1, 6, or 12)

        # Validate input
        if not x or not months or not isinstance(x, int) or not isinstance(months, int):
            return jsonify(
                {"success": False, "message": "Invalid input. Please provide valid 'x' and 'months' values."}), 400

        if months not in [1, 6, 12]:
            return jsonify({"success": False, "message": "Invalid 'months' value. Only 1, 6, and 12 are allowed."}), 400

        # Get the MySQL connection
        connection = mysql.connection
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to get the top X medicines based on their maximum sales within the given period
        query = f"""
            SELECT m.name AS medicine_name, m.id AS med_id, SUM(ms.quantity) AS total_sales
            FROM medicine_sales ms
            JOIN medicine m ON ms.medicine_id = m.id
            WHERE ms.sale_date >= CURDATE() - INTERVAL %s MONTH
            GROUP BY ms.medicine_id
            ORDER BY total_sales DESC
            LIMIT %s;
        """

        cursor.execute(query, (months, x))
        top_medicines_data = cursor.fetchall()
        cursor.close()

        if not top_medicines_data:
            return jsonify({"success": False, "message": "No data found for the given criteria."}), 404

        # Convert data to a serializable format
        top_medicines = [
            {
                "medicine_name": row["medicine_name"],
                "id": int(row["med_id"]),
                "total_sales": int(row["total_sales"])
            }
            for row in top_medicines_data
        ]

        return jsonify({"success": True, "top_medicines": top_medicines}), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Failed to retrieve top medicines", "error": str(e)}), 500



@analysis_bp.route('/sales_summary', methods=['GET'])
def general_sales_summary():
    try:
        # Get the MySQL connection
        connection = mysql.connection
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)

        # Query for total sales in the last month
        query_last_month_sales = """
            SELECT SUM(quantity) AS total_sales_last_month
            FROM medicine_sales
            WHERE sale_date >= CURDATE() - INTERVAL 1 MONTH;
        """
        cursor.execute(query_last_month_sales)
        last_month_sales = cursor.fetchone()['total_sales_last_month'] or 0

        # Query for total sales in the last six months
        query_last_six_months_sales = """
            SELECT SUM(quantity) AS total_sales_last_six_months
            FROM medicine_sales
            WHERE sale_date >= CURDATE() - INTERVAL 6 MONTH;
        """
        cursor.execute(query_last_six_months_sales)
        last_six_months_sales = cursor.fetchone()['total_sales_last_six_months'] or 0

        # Query for total sales in the last year
        query_last_year_sales = """
            SELECT SUM(quantity) AS total_sales_last_year
            FROM medicine_sales
            WHERE sale_date >= CURDATE() - INTERVAL 1 YEAR;
        """
        cursor.execute(query_last_year_sales)
        last_year_sales = cursor.fetchone()['total_sales_last_year'] or 0

        cursor.close()

        # Prepare the response
        response = {
            "success": True,
            "total_sales_last_month": int(last_month_sales),
            "total_sales_last_six_months": int(last_six_months_sales),
            "total_sales_last_year": int(last_year_sales)
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Failed to fetch general sales summary", "error": str(e)}), 500


@analysis_bp.route('/filtered_sales', methods=['POST'])
def filtered_sales():
    user_id = request.json.get('user_id')
    start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')
    medicine_name = request.json.get('medicine_name')
    barcode = request.json.get('barcode')

    if not user_id:
        return jsonify({"success": False, "message": "User ID is required"}), 400

    # Start with the base query for total sales by medicine
    query_base = """
        SELECT ms.medicine_id, SUM(ms.quantity) AS total_quantity, m.name AS medicine_name, m.barcode
        FROM medicine_sales ms
        JOIN medicine m ON ms.medicine_id = m.id
        WHERE ms.user_id = %s
    """
    query_params = [user_id]

    if start_date and end_date:
        query_base += " AND ms.sale_date BETWEEN %s AND %s"
        query_params.extend([start_date, end_date])

    if medicine_name:
        query_base += " AND m.name LIKE %s"
        query_params.append(f"%{medicine_name}%")

    if barcode:
        query_base += " AND m.barcode = %s"
        query_params.append(barcode)

    query_base += " GROUP BY ms.medicine_id, m.name, m.barcode"

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query_base, query_params)
        sales_data = cursor.fetchall()
        cursor.close()

        if not sales_data:
            return jsonify({"success": False, "message": "No sales data found"}), 404

        # Convert data to a serializable format
        sales_summary = [
            {
                "medicine_id": row["medicine_id"],
                "medicine_name": row["medicine_name"],
                "barcode": row["barcode"],
                "total_quantity": int(row["total_quantity"])
            }
            for row in sales_data
        ]

        return jsonify({"success": True, "sales_summary": sales_summary}), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Failed to filter sales", "error": str(e)}), 500



@analysis_bp.route('/most_popular_medicines', methods=['POST'])
def most_popular_medicines():
    user_id = request.json.get('user_id')
    start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')

    if not user_id:
        return jsonify({"success": False, "message": "User ID is required"}), 400

    query_base = """
        SELECT m.name AS medicine_name, SUM(ms.quantity) AS total_quantity
        FROM medicine_sales ms
        JOIN medicine m ON ms.medicine_id = m.id
        WHERE ms.user_id = %s
    """
    query_params = [user_id]

    if start_date and end_date:
        query_base += " AND ms.sale_date BETWEEN %s AND %s"
        query_params.extend([start_date, end_date])

    query_base += " GROUP BY m.name ORDER BY total_quantity DESC LIMIT 10"

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query_base, query_params)
        popular_medicines_data = cursor.fetchall()
        cursor.close()

        if not popular_medicines_data:
            return jsonify({"success": False, "message": "No popular medicines data found"}), 404

        most_popular_medicines = {
            medicine['medicine_name']: int(medicine['total_quantity'])
            for medicine in popular_medicines_data
        }

        return jsonify({"success": True, "most_popular_medicines": most_popular_medicines}), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Failed to retrieve most popular medicines", "error": str(e)}), 500



@analysis_bp.route('/sales_trend', methods=['POST'])
def sales_trend():
    user_id = request.json.get('user_id')
    start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')

    if not user_id:
        return jsonify({"success": False, "message": "User ID is required"}), 400

    query_base = """
        SELECT DATE_FORMAT(ms.sale_date, '%Y-%m') AS sale_month, SUM(ms.quantity) AS total_quantity
        FROM medicine_sales ms
        WHERE ms.user_id = %s
    """
    query_params = [user_id]

    if start_date and end_date:
        query_base += " AND ms.sale_date BETWEEN %s AND %s"
        query_params.extend([start_date, end_date])

    query_base += " GROUP BY sale_month ORDER BY sale_month"

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query_base, query_params)
        sales_trend_data = cursor.fetchall()
        cursor.close()

        if not sales_trend_data:
            return jsonify({"success": False, "message": "No sales trend data found"}), 404

        # Convert the result to a dictionary for JSON serialization
        sales_trend = {
            row['sale_month']: int(row['total_quantity'])
            for row in sales_trend_data
        }

        return jsonify({"success": True, "sales_trend": sales_trend}), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Failed to retrieve sales trend", "error": str(e)}), 500
