from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps
route_bp = Blueprint('route', __name__)
from models.Medicine import Medicine

def login_required(f):
    @wraps(f)  # This decorator preserves the original function's name and docstring
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('route.login'))
        return f(*args, **kwargs)
    return wrap


@route_bp.route('/image_process')
def image_process():
    return render_template('process_image.html')

@route_bp.route('/view_sales')
@login_required
def view_sales():
    return render_template('view_sale.html')


@route_bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')


# User Management Routes
@route_bp.route('/login')
def login():
    return render_template('pharmacy_user_login_page.html')


@route_bp.route('/register')
def register():
    return render_template('pharmacy_register.html')


@route_bp.route('/stock')
@login_required
def view_stock():
    return render_template('view_stock.html')


@route_bp.route('/stock_add')
@login_required
def add_stock_p():
    return render_template('buy_stock.html')


@route_bp.route('/medicines')
@login_required
def register_medicine():
    return render_template('register_medicine.html')


@route_bp.route('/medicines/<int:id>')
@login_required
def medicine_details(id):
    return render_template('medicine_details.html', medicine_id=id)


# Sales Management Routes
@route_bp.route('/sales')
@login_required
def sale_medicine():
    return render_template('sale_medicine_page.html')


# Sales Analysis Routes
@route_bp.route('/analysis')
@login_required
def sales_analysis():
    return render_template('sale_analysis_page.html')
