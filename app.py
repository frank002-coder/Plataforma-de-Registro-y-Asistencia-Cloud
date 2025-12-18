import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
# Obtenemos la URL de la variable de entorno de Render
database_url = os.environ.get('DATABASE_URL')

# Parche para corrección: Render/Neon a veces usan "postgres://" pero SQLAlchemy necesita "postgresql://"
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializamos la "herramienta" de base de datos
db = SQLAlchemy(app)

# --- DEFINICIÓN DE LA TABLA (MODELO) ---
class Participante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo,
            "fecha": self.fecha_registro.strftime("%Y-%m-%d %H:%M:%S")
        }

# --- CREAR TABLAS AL INICIAR ---
with app.app_context():
    db.create_all()

# --- RUTAS ---
@app.route('/')
def bienvenida():
    return "¡Hola! API conectada a Base de Datos Neon PostgreSQL 🚀"

@app.route('/api/v1/registro', methods=['POST'])
def registrar_participante():
    try:
        datos = request.json
        
        # Validacion simple
        if not datos or 'correo' not in datos:
            return jsonify({"error": "Faltan datos obligatorios"}), 400
            
        # Creamos el nuevo participante
        nuevo_participante = Participante(
            nombre=datos.get('nombre', 'Sin nombre'),
            correo=datos['correo']
        )
        
        # Guardamos en la Base de Datos Real
        db.session.add(nuevo_participante)
        db.session.commit()
        
        return jsonify({
            "mensaje": "Participante registrado exitosamente en la Nube",
            "participante": nuevo_participante.to_json()
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500