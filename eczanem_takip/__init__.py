from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS
mysql = MySQL()

def create_app():
    app = Flask(__name__)

    app.secret_key = 'abcdefgh'
    app.config['MYSQL_HOST'] = 'db'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'password'
    app.config['MYSQL_DB'] = 'eczanemtakipdb'
    app.config['MYSQL_CHARSET'] = 'utf8mb4'
    app.config['UPLOAD_FOLDER'] = 'uploads/'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    CORS(app)
    mysql.init_app(app)

    from medicine_app import medicine_bp
    from user_app import user_bp
    from stock_app import stock_bp
    from supplier_app import supplier_bp
    app.register_blueprint(medicine_bp, url_prefix='/api/medicines')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(stock_bp, url_prefix='/api/stock')
    app.register_blueprint(supplier_bp, url_prefix='/api/supplier')
    return app
