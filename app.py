from flask import Flask, request, redirect, url_for, render_template, jsonify
from werkzeug.utils import secure_filename
import os
import logging
from pymongo import MongoClient
from main import extraer_texto, extraer_nombre_y_direccion, buscar_en_base_datos

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configuración de la conexión a MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['documentos_db']
collection = db['imagenes']

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "El archivo está vacío"}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(file_path)

            # Extraer texto y datos de la imagen
            texto = extraer_texto(file_path)
            nombre, direccion = extraer_nombre_y_direccion(texto)

            # Guardar datos en MongoDB
            with open(file_path, 'rb') as img_file:
                collection.insert_one({
                    "nombre": nombre,
                    "direccion": direccion,
                    "imagen": img_file.read()
                })

            # Buscar coincidencias en la base de datos
            resultado = buscar_en_base_datos(nombre, direccion)

            return jsonify({
                "nombre": nombre,
                "direccion": direccion,
                "resultado": resultado
            })
        except Exception as e:
            logging.error(f"Error al procesar el archivo: {e}")
            return jsonify({"error": "Error al procesar el archivo"}), 500

@app.route('/datos')
def show_data():
    nombre = request.args.get('nombre', 'No disponible')
    domicilio = request.args.get('domicilio', 'No disponible')
    return render_template('datos.html', nombre=nombre, domicilio=domicilio)

if __name__ == '__main__':
    app.run(debug=True)
