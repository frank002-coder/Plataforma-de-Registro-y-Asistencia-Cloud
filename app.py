from flask import Flask, request, jsonify
from flask_cors import CORS
import os
# Para este ejemplo usaremos una lista en memoria como "Base de Datos de prueba"
# Cuando seas experto, aquí conectarás PostgreSQL.
base_de_datos_simulada = []

app = Flask(__name__)
CORS(app) # Esto permite que tu API sea llamada desde cualquier lugar (Google, tu web, etc)

# --- RUTA 1: RECIBIR DATOS (Lo que llama Google Forms) ---
@app.route('/api/v1/registro', methods=['POST'])
def registrar_participante():
    try:
        # El "mesero" recibe la nota con el pedido (los datos JSON)
        datos = request.json
        
        # Validamos que vengan los datos importantes
        if not datos or 'correo' not in datos:
            return jsonify({"error": "Faltan datos obligatorios"}), 400
            
        # Simulamos guardar en la base de datos
        # Aquí iría el código SQL: "INSERT INTO participantes..."
        nuevo_registro = {
            "id": len(base_de_datos_simulada) + 1,
            "nombre": datos.get('nombre', 'Anonimo'),
            "correo": datos.get('correo'),
            "evento": datos.get('evento', 'General'),
            "asistencia": False # Por defecto no ha asistido aún
        }
        base_de_datos_simulada.append(nuevo_registro)
        
        print(f"Nuevo registro guardado: {nuevo_registro['correo']}")
        return jsonify({"mensaje": "Guardado con éxito", "id": nuevo_registro['id']}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- RUTA 2: ENTREGAR REPORTES (Lo que llama tu Dashboard) ---
@app.route('/api/v1/reportes', methods=['GET'])
def obtener_reporte():
    # El mesero va a la cocina (base de datos) y trae la lista
    return jsonify({
        "total_registrados": len(base_de_datos_simulada),
        "participantes": base_de_datos_simulada
    }), 200

# --- RUTA DE SALUDO (Para probar que funciona) ---
@app.route('/')
def home():
    return "¡Hola! La API del Proyecto 21 está funcionando 🚀"

if __name__ == '__main__':
    # Esto permite correrlo en tu compu para probar
    app.run(debug=True, port=5000)