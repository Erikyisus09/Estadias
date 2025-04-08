# Instalación de dependencias

Este proyecto utiliza varias bibliotecas y herramientas para el procesamiento de imágenes, manejo de datos y conexión con MongoDB. A continuación, se describen los pasos para instalar las dependencias necesarias.

## Requisitos previos

1. **Python**: Asegúrate de tener Python 3.7 o superior instalado en tu sistema. Puedes descargarlo desde [python.org](https://www.python.org/).
2. **Tesseract OCR**: Instala Tesseract OCR en tu sistema. Puedes descargarlo desde [Tesseract OCR](https://github.com/tesseract-ocr/tesseract). Asegúrate de configurar la variable de entorno `TESSERACT_CMD` con la ruta al ejecutable de Tesseract.
3. **MongoDB**: Asegúrate de tener MongoDB instalado y en ejecución. Puedes descargarlo desde [MongoDB](https://www.mongodb.com/try/download/community).

## Instalación de dependencias de Python

1. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/Mac
   venv\Scripts\activate   # En Windows
   ```

2. Instala las dependencias listadas en el archivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

## Archivo `requirements.txt`

Asegúrate de que el archivo `requirements.txt` contenga las siguientes dependencias:

```
Flask
pymongo
Pillow
pytesseract
requests
twilio
Werkzeug
```

## Configuración de variables de entorno

Crea un archivo `.env` en la raíz del proyecto y define las siguientes variables:

```
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
MONGO_URI=mongodb://localhost:27017/
```

Asegúrate de ajustar las rutas y configuraciones según tu entorno.

## Ejecución del proyecto

1. Inicia la aplicación Flask:
   ```bash
   python main.py
   ```

2. Accede a la aplicación en tu navegador en `http://127.0.0.1:5000/`.

## Notas adicionales

- Si encuentras problemas con Tesseract OCR, verifica que esté correctamente instalado y configurado.
- Asegúrate de que MongoDB esté en ejecución antes de iniciar la aplicación.