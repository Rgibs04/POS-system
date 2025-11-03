from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import socket
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/pos.db'
app.config['SQLALCHEMY_BINDS'] = {
    'users': 'sqlite:///instance/users.db',
    'items': 'sqlite:///instance/items.db',
    'permissions': 'sqlite:///instance/permissions.db'
}
db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(db.Model):
    __bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    privilege = db.Column(db.String(20), nullable=False)  # student, kiosk_staff, teacher, admin
    rfid = db.Column(db.String(50), unique=True, nullable=True)

class Item(db.Model):
    __bind_key__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Permission(db.Model):
    __bind_key__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    permission = db.Column(db.String(50), nullable=False)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Kiosk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password_kiosk = db.Column(db.String(120), nullable=False)
    password_teacher = db.Column(db.String(120), nullable=False)
    password_admin = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='normal')  # normal, maintenance, error
    ip_address = db.Column(db.String(50), nullable=True)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

@app.route('/')
def index():
    if 'logged_in' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'admin':
            session['logged_in'] = True
            return redirect(url_for('index'))
        return 'Invalid password'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/api/users', methods=['GET', 'POST'])
def users():
    try:
        if request.method == 'POST':
            data = request.json
            if User.query.filter_by(rfid=data.get('rfid')).first() and data.get('rfid'):
                return jsonify({'error': 'RFID already assigned'}), 400
            user = User(username=data['username'], password=generate_password_hash(data['password']), privilege=data['privilege'], rfid=data.get('rfid'))
            db.session.add(user)
            db.session.commit()
            return jsonify({'message': 'User created'})
        users = User.query.all()
        return jsonify([{'id': u.id, 'username': u.username, 'privilege': u.privilege, 'rfid': u.rfid} for u in users])
    except Exception as e:
        logger.error(f"Error in users API: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/items', methods=['GET', 'POST'])
def items():
    try:
        if request.method == 'POST':
            data = request.json
            item = Item(name=data['name'], price=data['price'])
            db.session.add(item)
            db.session.commit()
            return jsonify({'message': 'Item added'})
        items = Item.query.all()
        return jsonify([{'id': i.id, 'name': i.name, 'price': i.price} for i in items])
    except Exception as e:
        logger.error(f"Error in items API: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/sales', methods=['GET', 'POST'])
def sales():
    try:
        if request.method == 'POST':
            data = request.json
            sale = Sale(user_id=data['user_id'], item_id=data['item_id'], quantity=data['quantity'], total_price=data['total_price'])
            db.session.add(sale)
            db.session.commit()
            return jsonify({'message': 'Sale recorded'})
        sales = Sale.query.all()
        return jsonify([{'id': s.id, 'user_id': s.user_id, 'item_id': s.item_id, 'quantity': s.quantity, 'total_price': s.total_price, 'timestamp': str(s.timestamp)} for s in sales])
    except Exception as e:
        logger.error(f"Error in sales API: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/kiosks', methods=['GET', 'POST'])
def kiosks():
    try:
        if request.method == 'POST':
            data = request.json
            kiosk = Kiosk(name=data['name'], password_kiosk=generate_password_hash('kiosk'), password_teacher=generate_password_hash('teacher'), password_admin=generate_password_hash('admin'))
            db.session.add(kiosk)
            db.session.commit()
            return jsonify({'message': 'Kiosk added'})
        kiosks = Kiosk.query.all()
        return jsonify([{'id': k.id, 'name': k.name, 'status': k.status, 'ip_address': k.ip_address} for k in kiosks])
    except Exception as e:
        logger.error(f"Error in kiosks API: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/kiosk/<int:id>', methods=['PUT'])
def update_kiosk(id):
    try:
        data = request.json
        kiosk = Kiosk.query.get(id)
        if not kiosk:
            return jsonify({'error': 'Kiosk not found'}), 404
        if 'status' in data:
            kiosk.status = data['status']
        if 'password_kiosk' in data:
            kiosk.password_kiosk = generate_password_hash(data['password_kiosk'])
        if 'password_teacher' in data:
            kiosk.password_teacher = generate_password_hash(data['password_teacher'])
        if 'password_admin' in data:
            kiosk.password_admin = generate_password_hash(data['password_admin'])
        if 'ip_address' in data:
            kiosk.ip_address = data['ip_address']
        db.session.commit()
        return jsonify({'message': 'Kiosk updated'})
    except Exception as e:
        logger.error(f"Error updating kiosk: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/discover', methods=['GET'])
def discover():
    ip = get_local_ip()
    return jsonify({'server_ip': ip, 'port': 5000})

if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
        logger.info("Database initialized")
        ip = get_local_ip()
        logger.info(f"Server starting on {ip}:5000")
        # Start discovery server in a thread
        import threading
        from discovery_server import discovery_server
        threading.Thread(target=discovery_server, daemon=True).start()
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
