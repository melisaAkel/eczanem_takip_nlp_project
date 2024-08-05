from flask import Flask, request, jsonify

from eczanem_takip.medicine_app import medicine_bp
from models import db
from models.User import User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@db:3306/eczanemtakipdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(medicine_bp, url_prefix='/api')
db.init_app(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        usernameormail = data.get('usernameormail')
        password = data.get('password')

        user = User.query.filter_by(username=usernameormail, password= password).first()
        if not user:
            user = User(mail=usernameormail, password=password).first()
        if user:
            return jsonify({"success": True, "message": "User found"})
        else:
            return jsonify({"success": False, "message": "User not found"})
    return jsonify({"success": False, "message": "Invalid request method"})


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        surname= data.get('surname')
        username = data.get('username')
        password = data.get('password')
        mail = data.get('mail')
        if not all([name, username, password, mail]):
            return jsonify({"success": False, "message": "Enter all the fields"})

            # Check if the user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"success": False, "message": "Username already exists"})
        elif User.query.filter_by(mail=mail).first():
            return jsonify({"success": False, "message": "Mail already exists"})
        try:
            user = User(name=name,surname= surname, username=username, password=password, mail=mail)
            db.session.add(user)
            db.session.commit()
            return jsonify({"success": True, "message": "Registered successfully",
                            "user": {"name": user.name, "username": user.username, "mail": user.mail}})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": "Registration failed", "error": str(e)})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
