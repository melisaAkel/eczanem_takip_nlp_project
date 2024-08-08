from flask import Blueprint, request, jsonify, render_template
from flask_mysqldb import MySQL
from models.User import User
from flask_cors import CORS

mysql = MySQL()

user_bp = Blueprint('user', __name__)
CORS(user_bp)


@user_bp.route('/register_page', methods=['GET'])
def register_page():
    return render_template("pharmacy_register.html")


@user_bp.route('login_page')
def login_page():
    return render_template('pharmacy_user_login_page.html')


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usernameoremail = data.get('usernameoremail')
    password = data.get('password')

    user = User.login(mysql.connection, usernameoremail, password)

    if user:
        return jsonify({"success": True, "message": "User found", "user": user.serialize()})
    else:
        return jsonify({"success": False, "message": "User not found"}), 404


# User registration
@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    surname = data.get('surname')
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not all([name, surname, username, password, email]):
        return jsonify({"success": False, "message": "Enter all the fields"}), 400

    existing_user = User.get_by_username(mysql.connection, username)
    if existing_user:
        return jsonify({"success": False, "message": "Username already exists"}), 409

    existing_email = User.get_by_email(mysql.connection, email)
    if existing_email:
        return jsonify({"success": False, "message": "Mail already exists"}), 409

    new_user = User(None, name, surname, username, email, password)
    try:
        User.add(mysql.connection, new_user)
        return jsonify({"success": True, "message": "Registered successfully",
                        "user": new_user.serialize()}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Registration failed", "error": str(e)}), 500
