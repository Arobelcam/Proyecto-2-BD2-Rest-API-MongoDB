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
### CONSULTAS

@app.route('/api/consultas')
def consultas_usuarios():
    # esta será la landing de consultas: match vs aggregation
    return render_template('consultas_usuarios.html')

### CONSULTAS A DOCUMENTOS
@app.route('/api/consultas/consul-documentos')
def consultas_documentos_usuarios():
    return render_template('consultas_documentos_usuarios.html')

@app.route('/api/consultas/consul-documentos')
def consultas_filtro_usuarios():
    return render_template('consultas_documentos_usuarios.html')

# — Filtro —
@app.route('/api/consultas/consul-documentos/filtro', methods=['GET', 'POST'])
def filtro_usuario():
    if request.method == 'POST':
        resultado = get_usuarios_filtros_servicio()
        return jsonify(resultado)
    return render_template('filtro_usuarios.html')


# — Proyección —
@app.route('/api/consultas/consul-documentos/proyeccion', methods=['GET', 'POST'])
def proyeccion_usuario():
    if request.method == 'POST':
        resultado = get_usuarios_proyeccion_servicio()
        return jsonify(resultado)
    return render_template('proyeccion_usuarios.html')


# — Ordenamiento —
@app.route('/api/consultas/consul-documentos/ordenamiento', methods=['GET', 'POST'])
def ordenamiento_usuario():
    if request.method == 'POST':
        resultado = get_usuarios_ordenamiento_servicio()
        return jsonify(resultado)
    return render_template('ordenamiento_usuarios.html')


# — Limit —
@app.route('/api/consultas/consul-documentos/limit', methods=['GET', 'POST'])
def limit_usuario():
    # Si es POST (desde formulario JSON) o viene el query param `limit`, devolvemos datos
    if request.method == 'POST' or 'limit' in request.args:
        resultado = get_usuarios_limit_servicio()
        return jsonify(resultado)
    # Si es GET sin limit, sirvo la página HTML
    return render_template('limit_usuarios.html')


# — Skip —
@app.route('/api/consultas/consul-documentos/skip', methods=['GET', 'POST'])
def skip_usuario():
    if request.method == 'POST' or 'skip' in request.args:
        resultado = get_usuarios_skip_servicio()
        return jsonify(resultado)
    # Si es GET sin skips, sirvo la página HTML
    return render_template('skip_usuarios.html')


### CONSULTAS POR AGREGACION
@app.route('/api/consultas/consul-agregacion')
def consultas_agregacion_usuarios():
    return render_template('consultas_agregacion_usuarios.html')

### simples
@app.route('/api/consultas/consul-agregacion/simple')
def agregacion_simple_usuarios():
    return render_template('agregacion_simple_usuarios.html')

# — Match —  
@app.route('/api/consultas/consul-agregacion/simple/match', methods=['GET', 'POST'])
def match_usuario():
    if request.method == 'POST' or bool(request.args):
        resultado = get_usuarios_match_servicio()
        return jsonify(resultado)
    return render_template('match_usuarios.html')

# — Group —  
@app.route('/api/consultas/consul-agregacion/simple/group', methods=['GET', 'POST'])
def group_usuario():
    if request.method == 'POST' or bool(request.args):
        resultado = get_usuarios_group_servicio()
        return jsonify(resultado)
    return render_template('group_usuarios.html')

# — Count — 
@app.route('/api/consultas/consul-agregacion/simple/count', methods=['GET', 'POST'])
def count_usuario():
    # Si llega body JSON o query params no vacíos, llamamos al servicio
    if request.method == 'POST' or bool(request.args):
        # tu servicio lee request.get_json() o request.args
        resultado = get_usuarios_count_servicio()
        return jsonify(resultado)
    return render_template('count_usuarios.html')

# — Distinct —
@app.route('/api/consultas/consul-agregacion/simple/distinct', methods=['GET', 'POST'])
def distinct_usuario():
    if request.method == 'POST' or bool(request.args):
        resultado = get_usuarios_distinct_servicio()
        return jsonify(resultado)
    return render_template('distinct_usuarios.html')


### agg pipeline
@app.route('/api/consultas/consul-agregacion/pipeline', methods=['GET', 'POST'])
def pipeline_usuarios():
    if request.method == 'POST':
        pipeline_definition = request.get_json()             # JSON con la definición de la pipeline
        resultado = aggregation_pipeline_servicio(pipeline_definition)
        return jsonify(resultado), 200

    # Si es GET, mostramos el formulario para construir la pipeline
    return render_template('pipeline_usuarios.html')

### arrays
@app.route('/api/consultas/consul-agregacion/arrays')
def agregacion_arrays_usuarios():
    return render_template('agregacion_arrays_usuarios.html')

### embedded
@app.route('/api/consultas/consul-agregacion/embedded')
def agregacion_embedded_usuarios():
    return render_template('agregacion_embedded_usuarios.html')

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