from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pytesseract
import cv2
import os
from placa_detection import procesar_imagen

# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # Cambia esto por una clave secreta real
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nueva_usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/images'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializa la base de datos y el login
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Configuración de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Ajusta esta ruta según sea necesario

# Modelos de la base de datos
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Puede ser 'admin' o 'guardia'

class Vehiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(50), nullable=False, unique=True)
    nombre_duenio = db.Column(db.String(150), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    telefono = db.Column(db.String(50), nullable=False)

@app.route('/eliminar_vehiculo/<int:id>', methods=['GET', 'POST'])
def eliminar_vehiculo(id):
    vehiculo = Vehiculo.query.get_or_404(id)
    if vehiculo:
        db.session.delete(vehiculo)
        db.session.commit()
    return redirect(url_for('ver_placas'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Bienvenido {user.username}!', 'success')
            return redirect(url_for('admin_dashboard') if user.role == 'admin' else url_for('guard_dashboard'))
        else:
            flash('Credenciales incorrectas', 'error')
    return render_template('login.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('No tienes permiso para acceder a esta página.', 'error')
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

@app.route('/guard_dashboard')
@login_required
def guard_dashboard():
    if current_user.role != 'guardia':
        flash('No tienes permiso para acceder a esta página.', 'error')
        return redirect(url_for('login'))
    return render_template('guard_dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login'))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/subir_imagen', methods=['GET', 'POST'])
@login_required
def subir_imagen():
    if current_user.role != 'guardia':
        flash('No tienes permiso para acceder a esta página.', 'error')
        return redirect(url_for('login'))

    placa_detectada = None

    if request.method == 'POST' and 'image' in request.files:
        file = request.files['image']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            placa_detectada = procesar_imagen(filepath)

            if placa_detectada:
                placa_detectada = ''.join(filter(str.isalnum, placa_detectada))
                vehiculo = Vehiculo.query.filter_by(placa=placa_detectada).first()

                if vehiculo:
                    mensaje = f'Placa {placa_detectada} detectada. Vehículo autorizado.'
                    flash(mensaje, 'success')
                else:
                    mensaje = f'Vehículo con placa {placa_detectada} no autorizado.'
                    flash(mensaje, 'error')
            else:
                flash('No se detectó una placa válida.', 'error')
        else:
            flash('Archivo no permitido o sin archivo.', 'error')

        return render_template('guard_dashboard.html', placa_detectada=placa_detectada)

    return render_template('guard_dashboard.html')

@app.route('/agregar_vehiculo', methods=['GET', 'POST'])
@login_required
def agregar_vehiculo():
    if current_user.role != 'admin':
        flash('No tienes permiso para acceder a esta página.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        placa = request.form['placa']
        nombre_duenio = request.form['nombre_duenio']
        edad = request.form['edad']
        telefono = request.form['telefono']

        if Vehiculo.query.filter_by(placa=placa).first():
            flash('El vehículo con esta placa ya está registrado.', 'error')
        else:
            nuevo_vehiculo = Vehiculo(
                placa=placa,
                nombre_duenio=nombre_duenio,
                edad=int(edad),
                telefono=telefono
            )
            db.session.add(nuevo_vehiculo)
            db.session.commit()
            flash('Vehículo registrado exitosamente.', 'success')

        return redirect(url_for('admin_dashboard'))

    return render_template('agregar_vehiculo.html')

@app.route('/ver_placas')
@login_required
def ver_placas():
    if current_user.role != 'admin':
        flash('No tienes permiso para acceder a esta página.', 'error')
        return redirect(url_for('login'))

    vehiculos = Vehiculo.query.all()
    return render_template('ver_placas.html', vehiculos=vehiculos)

@app.route('/registrar_clave', methods=['GET', 'POST'])
def registrar_clave():
    if request.method == 'POST':
        clave_ingresada = request.form['clave']

        if clave_ingresada == 'registrar1234':
            return redirect(url_for('registrar_guardia'))
        else:
            flash('Clave incorrecta. Intenta nuevamente.', 'error')
            return redirect(url_for('registrar_clave'))

    return render_template('registrar_clave.html')

@app.route('/registrar_guardia', methods=['GET', 'POST'])
def registrar_guardia():
    if request.method == 'POST':
        username = request.form['username']
        apellido = request.form['apellido']
        placa = request.form['placa']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        # Registrar al guardia directamente en la tabla User con el role 'guardia'
        nuevo_guardia = User(
            username=username,
            password=hashed_password,
            role='guardia'
        )

        db.session.add(nuevo_guardia)
        db.session.commit()

        flash('Guardia registrado correctamente', 'success')
        return redirect(url_for('login'))

    return render_template('registrar_guardia.html')

# Crear las tablas y un usuario administrador por defecto
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='nuevo_admin').first():
        hashed_password = generate_password_hash('admin1234')
        nuevo_admin = User(username='nuevo_admin', password=hashed_password, role='admin')
        db.session.add(nuevo_admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
