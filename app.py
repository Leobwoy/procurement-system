import sys
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.db import db  # Import db from models/db.py

from models.audit_log import AuditLog
from models.package import Package

# Add the current directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Initialize the Flask app
app = Flask(__name__)

# App Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///procurement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Procurement model
class Procurement(db.Model):
    __tablename__ = 'procurement'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    supplier = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    receiver = db.Column(db.String(100), nullable=False)
    package_type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256')  # Updated method

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/procurement', methods=['GET', 'POST'])
@login_required
def procurement():
    search_query = request.args.get('search', '').strip()
    filter_status = request.args.get('status', '')

    query = Procurement.query

    if search_query:
        query = query.filter(
            (Procurement.item_name.ilike(f"%{search_query}%")) |
            (Procurement.supplier.ilike(f"%{search_query}%")) |
            (Procurement.package_type.ilike(f"%{search_query}%"))
        )

    if filter_status:
        query = query.filter_by(status=filter_status)

    records = query.all()

    return render_template('procurement.html', records=records, search_query=search_query, filter_status=filter_status)


# Package Management Routes
@app.route('/package_tracking', methods=['GET'])
def package_tracking():
    status = request.args.get('status', '')
    tracking_results = None
    if status:
        tracking_results = Package.query.filter_by(status=status).all()
    return render_template('package_tracking.html', tracking_results=tracking_results)

@app.route('/package_list', methods=['GET'])
def package_list():
    packages = Package.query.all()
    return render_template('package_list.html', packages=packages)

@app.route('/reports', methods=['GET', 'POST'])
def reports():
    report = None
    if request.method == 'POST':
        report_type = request.form.get('report_type')
        if report_type == 'status':
            report = db.session.query(
                Package.item_name,
                Package.supplier,
                Package.quantity,
                Package.status
            ).order_by(Package.status).all()

        elif report_type == 'quantity':
            report = db.session.query(
                Package.item_name,
                Package.supplier,
                db.func.sum(Package.quantity).label('total_quantity')
            ).group_by(Package.supplier).all()

    return render_template('reports.html', report=report)


@app.route('/view_data', methods=['GET'])
def view_data():
    records = Procurement.query.all()
    return render_template('view_data.html', records=records)

#Add Procurement data
@app.route('/add_procurement', methods=['GET', 'POST'])
@login_required
def add_procurement():
    if request.method == 'POST':
        try:
            # Collect form data
            item_name = request.form.get('item_name')
            supplier = request.form.get('supplier')
            quantity = int(request.form.get('quantity'))
            receiver = request.form.get('receiver')
            package_type = request.form.get('package_type')
            status = request.form.get('status')

            # Add new record
            new_record = Procurement(
                item_name=item_name,
                supplier=supplier,
                quantity=quantity,
                receiver=receiver,
                package_type=package_type,
                status=status
            )
            db.session.add(new_record)

            # Add audit log
            audit_log = AuditLog(action=f"Added procurement record: {item_name}", user_id=current_user.id)
            db.session.add(audit_log)

            db.session.commit()
            flash('Procurement record added successfully!', 'success')
            return redirect(url_for('procurement'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding procurement record: {e}', 'error')
    
    return render_template('add_procurement.html')  # Render the form page

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    record = Procurement.query.get_or_404(id)
    if request.method == 'POST':
        # Fetch and validate form data
        record.item_name = request.form.get('item_name', record.item_name)
        record.supplier = request.form.get('supplier', record.supplier)
        record.quantity = request.form.get('quantity', record.quantity)
        record.receiver = request.form.get('receiver', record.receiver)
        record.package_type = request.form.get('package_type', record.package_type)
        record.status = request.form.get('status', record.status)
        
        db.session.commit()
        flash('Record updated successfully!', 'success')
        return redirect(url_for('view_data'))
    
    return render_template('edit.html', record=record)


@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    record = Procurement.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    flash('Record deleted successfully!', 'success')
    return redirect(url_for('procurement'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    records = []
    if request.method == 'POST':
        query = request.form.get('search_query', '')
        records = Procurement.query.filter(
            Procurement.item_name.contains(query) |
            Procurement.supplier.contains(query) |
            Procurement.receiver.contains(query)
        ).all()
    return render_template('procurement.html', records=records)

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure database tables are created
    app.run(debug=True)
