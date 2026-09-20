import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'TelegramShopBot'))

from flask import Flask, flash, redirect, render_template, request, session, url_for

from database import Order, Product, SessionLocal, User

app = Flask(__name__)
app.secret_key = os.getenv('ADMIN_WEB_SECRET', 'change-this-secret-key')

ADMIN_USERNAME = os.getenv('ADMIN_WEB_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_WEB_PASSWORD', 'admin123')
ADMIN_ALLOWED_IPS = {
    ip.strip()
    for ip in os.getenv('ADMIN_WEB_ALLOWED_IPS', '').split(',')
    if ip.strip()
}

STATUS_CHOICES = [
    'pending',
    'confirmed',
    'shipped',
    'delivered',
    'cancelled',
]


def get_client_ip():
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()

    real_ip = request.headers.get('X-Real-Ip', '').strip()
    if real_ip:
        return real_ip

    return request.remote_addr or 'unknown'


def is_whitelisted_client():
    return get_client_ip() in ADMIN_ALLOWED_IPS


def login_required():
    if session.get('admin_logged_in'):
        return True
    if is_whitelisted_client():
        session['admin_logged_in'] = True
        return True
    return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    if login_required():
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
def index():
    if not login_required():
        return redirect(url_for('login'))

    db = SessionLocal()
    try:
        total_orders = db.query(Order).count()
        total_revenue = sum(order.total_price or 0 for order in db.query(Order).all())
        total_products = db.query(Product).count()
        low_stock = db.query(Product).filter(Product.quantity_in_stock <= 10).count()

        orders = db.query(Order).order_by(Order.created_at.desc()).all()
        products = db.query(Product).order_by(Product.category, Product.name).all()

        return render_template(
            'dashboard.html',
            orders=orders,
            products=products,
            total_orders=total_orders,
            total_revenue=total_revenue,
            total_products=total_products,
            low_stock=low_stock,
            status_choices=STATUS_CHOICES,
        )
    finally:
        db.close()


@app.route('/orders/<int:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    if not login_required():
        return redirect(url_for('login'))

    new_status = request.form.get('status')
    if new_status not in STATUS_CHOICES:
        flash('Invalid order status')
        return redirect(url_for('index'))

    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = new_status
            db.commit()
            flash(f'Order #{order.order_number} updated to {new_status}')
    finally:
        db.close()

    return redirect(url_for('index'))


@app.route('/products/<int:product_id>/stock', methods=['POST'])
def update_product_stock(product_id):
    if not login_required():
        return redirect(url_for('login'))

    stock_value = request.form.get('quantity_in_stock', '').strip()
    try:
        quantity = int(stock_value)
    except ValueError:
        flash('Stock value must be a number')
        return redirect(url_for('index'))

    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            product.quantity_in_stock = quantity
            db.commit()
            flash(f'Updated stock for {product.name} to {quantity}')
    finally:
        db.close()

    return redirect(url_for('index'))


if __name__ == '__main__':
    host = os.getenv('ADMIN_WEB_HOST', '127.0.0.1')
    port = int(os.getenv('PORT', os.getenv('ADMIN_WEB_PORT', 5001)))
    debug = os.getenv('FLASK_DEBUG', '0').lower() in {'1', 'true', 'yes'}
    app.run(host=host, port=port, debug=debug)
