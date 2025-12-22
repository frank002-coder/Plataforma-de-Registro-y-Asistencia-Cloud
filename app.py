import os
import csv
import io
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
database_url = os.environ.get('DATABASE_URL')
# Parche para compatibilidad con Render/Neon
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELO (TABLA) ---
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

# Creación de tablas al iniciar
with app.app_context():
    db.create_all()

# --- RUTA 1: BIENVENIDA (Health Check) ---
@app.route('/')
def bienvenida():
    return "¡Hola! API funcionando con Base de Datos y Reportes 🚀"

# --- RUTA 2: REGISTRO (Para el Formulario) ---
@app.route('/api/v1/registro', methods=['POST'])
def registrar_participante():
    try:
        datos = request.json
        if not datos or 'correo' not in datos:
            return jsonify({"error": "Faltan datos obligatorios"}), 400
            
        nuevo_participante = Participante(
            nombre=datos.get('nombre', 'Sin nombre'),
            correo=datos['correo']
        )
        
        db.session.add(nuevo_participante)
        db.session.commit()
        
        return jsonify({
            "mensaje": "Participante registrado exitosamente",
            "participante": nuevo_participante.to_json()
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- RUTA 3: DESCARGAR REPORTE (Para el Admin) ---
# Esta es la parte nueva que genera el Excel/CSV
@app.route('/api/v1/reporte', methods=['GET'])
def descargar_reporte():
    try:
        # 1. Consultamos TODOS los participantes
        participantes = Participante.query.all()

        # 2. Preparamos el archivo en memoria
        si = io.StringIO()
        cw = csv.writer(si)
        
        # 3. Encabezados
        cw.writerow(['ID', 'Nombre Completo', 'Correo Electrónico', 'Fecha de Registro (UTC)'])

        # 4. Datos
        for p in participantes:
            cw.writerow([p.id, p.nombre, p.correo, p.fecha_registro])

        # 5. Respuesta de descarga
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=reporte_asistencia.csv"
        output.headers["Content-type"] = "text/csv"
        
        return output

    except Exception as e:
        return jsonify({"error": str(e)}), 500