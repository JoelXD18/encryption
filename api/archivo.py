from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
import base64, hashlib, pyfiglet

app = Flask(__name__)
FIRMA = "Joel"

def generar_clave(password: str) -> bytes:
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def generar_ascii_firma() -> bytes:
    ascii_banner = pyfiglet.figlet_format(FIRMA)
    return ascii_banner.encode() + b"\n--ENCRYPTED FILE START--\n"

def encriptar_archivo(file_bytes, filename, password):
    clave = generar_clave(password)
    fernet = Fernet(clave)
    datos_encriptados = fernet.encrypt(file_bytes)
    datos_finales = f"FILENAME:{filename}\n".encode() + generar_ascii_firma() + datos_encriptados
    return datos_finales

def desencriptar_archivo(file_bytes, password):
    clave = generar_clave(password)
    fernet = Fernet(clave)
    try:
        first_line, resto = file_bytes.split(b"\n", 1)
        if not first_line.startswith(b"FILENAME:"):
            raise ValueError("No se encontró la extensión original")
        nombre_original = first_line[len(b"FILENAME:"):].decode()
        _, datos_encriptados = resto.split(b"--ENCRYPTED FILE START--\n", 1)
        datos_originales = fernet.decrypt(datos_encriptados)
    except Exception as e:
        return None, str(e)
    return datos_originales, nombre_original

@app.route("/procesar", methods=["POST"])
def procesar():
    archivo = request.files.get("archivo")
    password = request.form.get("password")
    accion = request.form.get("accion")

    if not archivo or not password or not accion:
        return jsonify({"error": "Falta archivo, contraseña o acción"}), 400

    file_bytes = archivo.read()
    filename = archivo.filename

    if accion == "encriptar":
        resultado = encriptar_archivo(file_bytes, filename, password)
        return jsonify({
            "filename": filename + ".enc",
            "filedata": resultado.hex()
        })
    elif accion == "desencriptar":
        datos_originales, nombre = desencriptar_archivo(file_bytes, password)
        if datos_originales is None:
            return jsonify({"error": nombre}), 400
        return jsonify({
            "filename": "DEC_" + nombre,
            "filedata": datos_originales.hex()
        })
    else:
        return jsonify({"error": "Acción desconocida"}), 400
