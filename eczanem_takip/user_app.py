from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from flask_mysqldb import MySQL
from models.User import User
from flask_cors import CORS

mysql = MySQL()

user_bp = Blueprint('user', __name__)
CORS(user_bp)

@user_bp.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove the user_id from session
    return redirect(url_for('route.login'))

@user_bp.route('/get_user_id', methods=['GET'])
def get_user_id():
    user_id = session.get('user_id')
    if user_id:
        return jsonify({"success": True, "user_id": user_id})
    else:
        return jsonify({"success": False, "message": "User not logged in"}), 401


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usernameoremail = data.get('usernameoremail')
    password = data.get('password')

    user = User.login(mysql.connection, usernameoremail, password)

    if user:
        session['user_id'] = user.id
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
