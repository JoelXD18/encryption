from flask import Flask, request, send_file, render_template
from cryptography.fernet import Fernet
import base64, hashlib, pyfiglet, io, os

# Flask apunta a la raíz para encontrar index.html
app = Flask(__name__, template_folder=".")

FIRMA = "Joel"

def generar_clave(password: str) -> bytes:
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def generar_ascii_firma() -> bytes:
    ascii_banner = pyfiglet.figlet_format(FIRMA)
    return ascii_banner.encode() + b"\n--ENCRYPTED FILE START--\n"

def encriptar_archivo(file_stream, filename, password):
    clave = generar_clave(password)
    fernet = Fernet(clave)
    datos = file_stream.read()
    datos_encriptados = fernet.encrypt(datos)
    datos_finales = f"FILENAME:{filename}\n".encode() + generar_ascii_firma() + datos_encriptados
    return datos_finales

def desencriptar_archivo(file_stream, password):
    clave = generar_clave(password)
    fernet = Fernet(clave)
    contenido = file_stream.read()
    try:
        first_line, resto = contenido.split(b"\n", 1)
        if not first_line.startswith(b"FILENAME:"):
            raise ValueError("No se encontró la extensión original")
        nombre_original = first_line[len(b"FILENAME:"):].decode()
        _, datos_encriptados = resto.split(b"--ENCRYPTED FILE START--\n", 1)
        datos_originales = fernet.decrypt(datos_encriptados)
    except Exception as e:
        return None, str(e)
    return datos_originales, nombre_original

@app.route("/", methods=["GET", "POST"])
def index():
    mensaje = ""

    if request.method == "POST":
        password = request.form.get("password")
        accion = request.form.get("accion")
        archivo = request.files.get("archivo")

        if not password or not archivo:
            mensaje = "❌ Debes ingresar contraseña y seleccionar un archivo"
        else:
            if accion == "encriptar":
                datos_finales = encriptar_archivo(archivo.stream, archivo.filename, password)
                return send_file(
                    io.BytesIO(datos_finales),
                    download_name=archivo.filename + ".enc",
                    as_attachment=True
                )
            elif accion == "desencriptar":
                datos_originales, nombre = desencriptar_archivo(archivo.stream, password)
                if datos_originales is None:
                    mensaje = f"❌ Error: {nombre}"
                else:
                    return send_file(
                        io.BytesIO(datos_originales),
                        download_name="DEC_" + nombre,
                        as_attachment=True
                    )

    return render_template("index.html", mensaje=mensaje)

# Nota: no usamos app.run() en Vercel; el servidor lo maneja
