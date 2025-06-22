# app.py (modificación para usar tokens según cuenta seleccionada)
import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for

# Cargar variables del archivo uno.env
load_dotenv("uno.env")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

app = Flask(__name__)
CLAVE_SECRETA = "superclave2025"

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == CLAVE_SECRETA:
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', error="Contraseña incorrecta")
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    cuenta = request.args.get('cuenta', 'sportup')
    nombre_archivo_token = f"token_{cuenta}.txt"

    try:
        with open(nombre_archivo_token, "r") as f:
            access_token = f.read().strip()
    except FileNotFoundError:
        return "No se encontró el token. Iniciá sesión desde /auth primero.", 400

    headers = {"Authorization": f"Bearer {access_token}"}
    user_data = requests.get("https://api.mercadolibre.com/users/me", headers=headers).json()
    user_id = user_data.get("id")

    if not user_id:
        return "No se pudo obtener el user_id. ¿El token expiró?", 400

    publicaciones_url = f"https://api.mercadolibre.com/users/{user_id}/items/search"
    res = requests.get(publicaciones_url, headers=headers)
    ids = res.json().get("results", [])
    print("IDS OBTENIDOS:", ids)


    productos = []
    for id_producto in ids[:20]:
        producto_url = f"https://api.mercadolibre.com/items/{id_producto}"
        r = requests.get(producto_url)
        data = r.json()
        productos.append({
            "id": data.get("id"),
            "title": data.get("title"),
            "price": data.get("price"),
            "available_quantity": data.get("available_quantity")
        })

    return render_template("dashboard.html", productos=productos)

@app.route('/auth')
def auth():
    return redirect(
        f"https://auth.mercadolibre.com.ar/authorization?"
        f"response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    )

@app.route('/callback')
def callback():
    code = request.args.get("code")
    if not code:
        return "No se recibió el código de autorización", 400

    token_url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, data=payload, headers=headers)
    data = response.json()

    if "access_token" not in data:
        return f"Error al obtener el token: {data}", 400

    access_token = data["access_token"]
    user_info = requests.get("https://api.mercadolibre.com/users/me", headers={"Authorization": f"Bearer {access_token}"}).json()
    nickname = user_info.get("nickname", "unknown").lower()

    # Identificar cuenta y guardar token según nickname
    cuenta = "sportup"
    if "estefi" in nickname:
        cuenta = "estefania"
    elif "david" in nickname:
        cuenta = "david"

    with open(f"token_{cuenta}.txt", "w") as f:
        f.write(access_token)

    return redirect(url_for("dashboard", cuenta=cuenta))


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
