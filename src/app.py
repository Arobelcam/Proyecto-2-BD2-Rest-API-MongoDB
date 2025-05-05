from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os

from config.mongodb import mongo
from Rutas.usuario import usuario
from Rutas.restaurante import restaurante
from Rutas.menu import menu
from Rutas.pedidos import pedidos
from Rutas.reseñas import reseñas
from services.usuario import *

app = Flask(__name__, 
            static_folder='static', 
            template_folder='templates')

load_dotenv()
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo.init_app(app)

app.register_blueprint(usuario, url_prefix='/api')
app.register_blueprint(restaurante, url_prefix='/restaurante')
app.register_blueprint(menu, url_prefix='/menu')
app.register_blueprint(pedidos, url_prefix='/pedidos')
app.register_blueprint(reseñas, url_prefix='/reseñas')

@app.route('/')
def index():
    return render_template('index.html')

### LANDING PAGE USUARIOS
@app.route('/api')
def home_usuarios():
    return render_template('usuarios.html')

@app.route('/api/crear', methods=['GET', 'POST'])
def crear_usuario():
    if request.method == 'POST':
        data = request.get_json()         # JSON enviado desde el cliente
        resultado = crear_usuarios_servicio(data)
        # Puedes devolver un status code 201 si creaste con éxito
        return jsonify(resultado), 201
    return render_template('crear_usuario.html')

@app.route('/api/consultas')
def consultas_usuarios():
    # esta será la landing de consultas: match vs aggregation
    return render_template('consultas_usuarios.html')

@app.route('/api/actualizar', methods=['GET', 'PUT'])
def actualizar_usuario():
    if request.method == 'PUT':
        data = request.get_json()  # Debe contener usuario_id y campos nuevos
        resultado = actualizar_usuarios_servicio(data)
        return jsonify(resultado), 200
    return render_template('actualizar_usuario.html')

@app.route('/api/eliminar', methods=['GET', 'DELETE'])
def eliminar_usuario():
    if request.method == 'DELETE':
        data = request.get_json()              # Debe contener usuario_id o lista de IDs
        resultado = eliminar_usuarios_servicio(data)
        return jsonify(resultado), 200
    return render_template('eliminar_usuario.html')

###LANDING PAGE RESTAURANTES
@app.route('/restaurantes')
def home_restaurantes():
    return render_template('restaurantes.html')

@app.route('/menu')
def home_menu():
    return render_template('menu.html')

@app.route('/pedidos')
def home_pedidos():
    return render_template('pedidos.html')

@app.route('/reseñas')
def home_resenas():
    return render_template('resenas.html')



if __name__ == "__main__":
    app.run(debug=True)