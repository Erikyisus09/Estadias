# Importamos las librerías necesarias para el procesamiento de imágenes, manejo de datos y conexión con MongoDB
# También configuramos el registro de logs para depurar errores
from PIL import Image
import pytesseract
import re
import logging
import os
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from twilio.twiml.messaging_response import MessagingResponse
from io import BytesIO
import requests
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.INFO)

# Configuración de Tesseract para OCR (reconocimiento óptico de caracteres)
# Asegúrate de que Tesseract esté instalado y configurado correctamente
pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_CMD', r'C:\Program Files\Tesseract-OCR\tesseract.exe')

app = Flask(__name__)

# Configuración de la carpeta para almacenar imágenes subidas temporalmente
# Si no existe, se crea automáticamente
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuración de la conexión a MongoDB
# Aquí se almacenarán las imágenes y los datos extraídos
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['documentos_db']
collection = db['imagenes']

# Función para extraer texto de una imagen usando OCR
# Convierte la imagen en texto legible para extraer información relevante
def extraer_texto(imagen_path: str) -> str:
    try:
        img = Image.open(imagen_path)
        texto = pytesseract.image_to_string(img, lang='spa')
        return texto
    except Exception as e:
        logging.error(f"Error al procesar la imagen {imagen_path}: {e}")
        return ""

# Función para extraer el nombre y la dirección del texto extraído
# Utiliza expresiones regulares para buscar patrones específicos en el texto
def extraer_nombre_y_direccion(texto: str) -> tuple:
    patron_nombre = r'Nombre:\s*(.+)'
    patron_direccion = r'Dirección:\s*(.+)'

    nombre = re.search(patron_nombre, texto)
    direccion = re.search(patron_direccion, texto)

    return nombre.group(1).strip() if nombre else "No se encontró el nombre", \
           direccion.group(1).strip() if direccion else "No se encontró la dirección"

# Función para preprocesar imágenes
# Ajusta el tamaño, formato y calidad de las imágenes antes de procesarlas
def preprocesar_imagen(imagen_path: str) -> str:
    try:
        img = Image.open(imagen_path)
        img = img.convert('RGB')
        img = img.resize((1024, 1024))  # Ajustar tamaño
        preprocessed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"preprocessed_{os.path.basename(imagen_path)}")
        img.save(preprocessed_path, format='JPEG', quality=85)
        return preprocessed_path
    except Exception as e:
        logging.error(f"Error al preprocesar la imagen {imagen_path}: {e}")
        return imagen_path

# Función para buscar coincidencias en la base de datos
# Verifica si el nombre y la dirección ya existen en MongoDB
def buscar_en_base_datos(nombre: str, direccion: str) -> dict:
    try:
        resultado = collection.find_one({"nombre": nombre, "direccion": direccion})
        return resultado if resultado else {"mensaje": "No se encontraron coincidencias"}
    except Exception as e:
        logging.error(f"Error al buscar en la base de datos: {e}")
        return {"mensaje": "Error en la búsqueda"}

# Ruta principal para la página de inicio
# Renderiza un archivo HTML básico (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para subir archivos manualmente
# Permite procesar imágenes subidas desde un formulario web
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "El archivo está vacío"}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        try:
            file.save(file_path)
            texto = extraer_texto(file_path)
            nombre, direccion = extraer_nombre_y_direccion(texto)
            return jsonify({"nombre": nombre, "direccion": direccion})
        except Exception as e:
            logging.error(f"Error al procesar el archivo: {e}")
            return jsonify({"error": "Error al procesar el archivo"}), 500

# Ruta para el webhook de WhatsApp
# Recibe imágenes enviadas por los usuarios a través de WhatsApp
# Descarga la imagen, la preprocesa, extrae texto, guarda los datos en MongoDB y busca coincidencias
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    response = MessagingResponse()
    if 'MediaUrl0' in request.form:
        media_url = request.form['MediaUrl0']
        file_name = os.path.join(app.config['UPLOAD_FOLDER'], 'whatsapp_image.jpg')

        try:
            img_data = requests.get(media_url).content
            with open(file_name, 'wb') as handler:
                handler.write(img_data)

            preprocessed_path = preprocesar_imagen(file_name)
            texto = extraer_texto(preprocessed_path)
            nombre, direccion = extraer_nombre_y_direccion(texto)

            with open(preprocessed_path, 'rb') as img_file:
                collection.insert_one({
                    "nombre": nombre,
                    "direccion": direccion,
                    "imagen": img_file.read()
                })

            resultado = buscar_en_base_datos(nombre, direccion)
            response.message(f"Nombre: {nombre}\nDirección: {direccion}\nResultado: {resultado}")

        except Exception as e:
            logging.error(f"Error al procesar la imagen de WhatsApp: {e}")
            response.message("Hubo un error al procesar tu imagen. Por favor, intenta nuevamente.")
    else:
        response.message("Por favor, envía una imagen para procesar.")

    return str(response)

# Punto de entrada principal para ejecutar la aplicación Flask
# Ejecuta el servidor en modo de depuración para facilitar el desarrollo
if __name__ == "__main__":
    app.run(debug=True)
