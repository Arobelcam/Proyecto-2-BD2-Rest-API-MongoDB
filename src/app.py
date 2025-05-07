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
from services.restaurante import *
from services.menu import *
from services.pedidos import *
from services.reseñas import *

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

### LANDING PAGE USUARIOS -----------------------------------------------------------------------------------------------------
@app.route('/api')
def home_usuarios():
    return render_template('t_usuarios/usuarios.html')

@app.route('/api/crear', methods=['GET', 'POST'])
def crear_usuario():
    if request.method == 'POST':
        data = request.get_json()         # JSON enviado desde el cliente
        resultado = crear_usuarios_servicio(data)
        # Puedes devolver un status code 201 si creaste con éxito
        return jsonify(resultado), 201
    return render_template('t_usuarios/crear_usuario.html')
### CONSULTAS

@app.route('/api/consultas')
def consultas_usuarios():
    # esta será la landing de consultas: match vs aggregation
    return render_template('t_usuarios/consultas_usuarios.html')

### CONSULTAS A DOCUMENTOS
@app.route('/api/consultas/consul-documentos')
def consultas_documentos_usuarios():
    return render_template('t_usuarios/consultas_documentos_usuarios.html')

# — Filtro —
@app.route('/api/consultas/consul-documentos/filtro', methods=['GET', 'POST'])
def filtro_usuario():
    if request.method == 'POST':
        resultado = get_usuarios_filtros_servicio()
        return jsonify(resultado)
    return render_template('t_usuarios/filtro_usuarios.html')


# — Proyección —
@app.route('/api/consultas/consul-documentos/proyeccion', methods=['GET', 'POST'])
def proyeccion_usuario():
    if request.method == 'POST':
        resultado = get_usuarios_proyeccion_servicio()
        return jsonify(resultado)
    return render_template('t_usuarios/proyeccion_usuarios.html')


# — Ordenamiento —
@app.route('/api/consultas/consul-documentos/ordenamiento', methods=['GET', 'POST'])
def ordenamiento_usuario():
    if request.method == 'POST':
        resultado = get_usuarios_ordenamiento_servicio()
        return jsonify(resultado)
    return render_template('t_usuarios/ordenamiento_usuarios.html')

# — Limit —
@app.route('/api/consultas/consul-documentos/limit', methods=['GET', 'POST'])
def limit_usuario():
    # Si es POST (desde formulario JSON) o viene el query param `limit`, devolvemos datos
    if request.method == 'POST' or 'limit' in request.args:
        resultado = get_usuarios_limit_servicio()
        return jsonify(resultado)
    # Si es GET sin limit, sirvo la página HTML
    return render_template('t_usuarios/limit_usuarios.html')

# — Skip —
@app.route('/api/consultas/consul-documentos/skip', methods=['GET', 'POST'])
def skip_usuario():
    if request.method == 'POST' or 'skip' in request.args:
        resultado = get_usuarios_skip_servicio()
        return jsonify(resultado)
    # Si es GET sin skips, sirvo la página HTML
    return render_template('t_usuarios/skip_usuarios.html')


### CONSULTAS POR AGREGACION
@app.route('/api/consultas/consul-agregacion')
def consultas_agregacion_usuarios():
    return render_template('t_usuarios/consultas_agregacion_usuarios.html')

### simples
@app.route('/api/consultas/consul-agregacion/simple')
def agregacion_simple_usuarios():
    return render_template('t_usuarios/agregacion_simple_usuarios.html')

# — Match —  
@app.route('/api/consultas/consul-agregacion/simple/match', methods=['GET', 'POST'])
def match_usuario():
    if request.method == 'POST' or bool(request.args):
        resultado = get_usuarios_match_servicio()
        return jsonify(resultado)
    return render_template('t_usuarios/match_usuarios.html')

# — Group —  
@app.route('/api/consultas/consul-agregacion/simple/group', methods=['GET', 'POST'])
def group_usuario():
    if request.method == 'POST' or bool(request.args):
        resultado = get_usuarios_group_servicio()
        return jsonify(resultado)
    return render_template('t_usuarios/group_usuarios.html')

# — Count — 
@app.route('/api/consultas/consul-agregacion/simple/count', methods=['GET', 'POST'])
def count_usuario():
    # Si llega body JSON o query params no vacíos, llamamos al servicio
    if request.method == 'POST' or bool(request.args):
        # tu servicio lee request.get_json() o request.args
        resultado = get_usuarios_count_servicio()
        return jsonify(resultado)
    return render_template('t_usuarios/count_usuarios.html')

# — Distinct —
@app.route('/api/consultas/consul-agregacion/simple/distinct', methods=['GET', 'POST'])
def distinct_usuario():
    if request.method == 'POST' or bool(request.args):
        resultado = get_usuarios_distinct_servicio()
        return jsonify(resultado)
    return render_template('t_usuarios/distinct_usuarios.html')


### agg pipeline
@app.route('/api/consultas/consul-agregacion/pipeline', methods=['GET','POST'])
def pipeline_usuarios():
    if request.method == 'POST':
        # No necesitas leer aquí request.get_json() ni pasarlo al servicio
        resultado = aggregation_pipeline_servicio()
        return jsonify(resultado), 200

    # GET: renderizamos el formulario
    return render_template('t_usuarios/pipeline_usuarios.html')

### arrays
@app.route('/api/consultas/consul-agregacion/arrays')
def agregacion_arrays_usuarios():
    return render_template('t_usuarios/agregacion_arrays_usuarios.html')

# — Push —
@app.route('/api/consultas/consul-agregacion/arrays/push', methods=['GET', 'POST'])
def push_usuario():
    if request.method == 'POST':
        resultado = push_usuario_servicio()
        if isinstance(resultado, tuple):
            payload, code = resultado
            return jsonify(payload), code
        return jsonify(resultado), 200
    return render_template('t_usuarios/push_usuarios.html')

# — Pull —
@app.route('//api/consultas/consul-agregacion/arrays/pull', methods=['GET', 'POST'])
def pull_usuario():
    if request.method == 'POST':
        resultado = pull_usuario_servicio()
        if isinstance(resultado, tuple):
            payload, code = resultado
            return jsonify(payload), code
        return jsonify(resultado), 200
    return render_template('t_usuarios/pull_usuarios.html')

# — AddToSet —
@app.route('/api/consultas/consul-agregacion/arrays/addToSet', methods=['GET', 'POST'])
def add_to_set_usuario():
    if request.method == 'POST':
        resultado = add_to_set_usuario_servicio()
        if isinstance(resultado, tuple):
            payload, code = resultado
            return jsonify(payload), code
        return jsonify(resultado), 200
    return render_template('t_usuarios/add_to_set_usuarios.html')

### embedded
@app.route('/api/consultas/consul-agregacion/embedded')
def agregacion_embedded_usuarios():
    return render_template('t_usuarios/agregacion_embedded_usuarios.html')

@app.route('/api/consultas/consul-agregacion/embedded/project', methods=['GET', 'POST'])
def project_usuarios():
    if request.method == 'POST':
        # Ejecuta el servicio y devuelve JSON
        resultado = project_usuario_servicio()
        return jsonify(resultado)
    # Si es GET, simplemente renderiza el formulario
    return render_template('t_usuarios/project_usuarios.html')

@app.route('/api/consultas/consul-agregacion/embedded/unwind', methods=['GET', 'POST'])
def unwind_usuarios():
    if request.method == 'POST':
        resultado = unwind_usuario_servicio()
        return jsonify(resultado)
    return render_template('t_usuarios/unwind_usuarios.html')

@app.route('/api/consultas/consul-agregacion/embedded/lookup', methods=['GET', 'POST'])
def lookup_usuarios():
    if request.method == 'POST':
        resultado = lookup_usuario_servicio()
        return jsonify(resultado)
    return render_template('t_usuarios/lookup_usuarios.html')

#Actualizar usuarios
@app.route('/api/actualizar', methods=['GET', 'PUT'])
def actualizar_usuario():
    if request.method == 'PUT':
        data = request.get_json()  # Debe contener usuario_id y campos nuevos
        resultado = actualizar_usuarios_servicio(data)
        return jsonify(resultado), 200
    return render_template('t_usuarios/actualizar_usuario.html')

#Eliminar usuarios
@app.route('/api/eliminar', methods=['GET', 'DELETE'])
def eliminar_usuario():
    if request.method == 'DELETE':
        data = request.get_json()              # Debe contener usuario_id o lista de IDs
        resultado = eliminar_usuarios_servicio(data)
        return jsonify(resultado), 200
    return render_template('t_usuarios/eliminar_usuario.html')



### LANDING PAGE RESTAURANTES -----------------------------------------------------------------------------------------
@app.route('/restaurantes')
def home_restaurantes():
    return render_template('t_restaurantes/restaurantes.html')

@app.route('/restaurantes/crear_r', methods=['GET', 'POST'])
def crear_restaurante():
    if request.method == 'POST':
        data = request.get_json()         # JSON enviado desde el cliente
        resultado = crear_restaurantes_servicio(data)
        # Puedes devolver un status code 201 si creaste con éxito
        return jsonify(resultado), 201
    return render_template('t_restaurantes/crear_restaurantes.html')
### CONSULTAS

@app.route('/restaurantes/consultas_r')
def consultas_restaurantes():
    # esta será la landing de consultas: match vs aggregation
    return render_template('t_restaurantes/consultas_restaurantes.html')

### CONSULTAS A DOCUMENTOS
@app.route('/restaurantes/consultas_r/consul-documentos_r')
def consultas_documentos_restaurantes():
    return render_template('t_restaurantes/consultas_documentos_restaurantes.html')

# — Filtro —
@app.route('/restaurantes/consultas_r/consul-documentos_r/filtro_r', methods=['GET', 'POST'])
def filtro_restaurante():
    if request.method == 'POST':
        resultado = get_restaurantes_filtros_servicio()
        return jsonify(resultado)
    return render_template('t_restaurantes/filtro_restaurantes.html')

# — Proyección —
@app.route('/restaurantes/consultas_r/consul-documentos_r/proyeccion_r', methods=['GET', 'POST'])
def proyeccion_restaurante():
    if request.method == 'POST':
        resultado = get_restaurantes_proyeccion_servicio()
        return jsonify(resultado)
    return render_template('t_restaurantes/proyeccion_restaurantes.html')

# — Ordenamiento —
@app.route('/restaurantes/consultas_r/consul-documentos_r/ordenamiento_r', methods=['GET', 'POST'])
def ordenamiento_restaurante():
    if request.method == 'POST':
        resultado = get_restaurantes_ordenamiento_servicio()
        return jsonify(resultado)
    return render_template('t_restaurantes/ordenamiento_restaurantes.html')

# — Limit —
@app.route('/restaurantes/consultas_r/consul-documentos_r/limit_r', methods=['GET', 'POST'])
def limit_restaurante():
    # Si es POST (desde formulario JSON) o viene el query param `limit`, devolvemos datos
    if request.method == 'POST' or 'limit' in request.args:
        resultado = get_restaurantes_limit_servicio()
        return jsonify(resultado)
    # Si es GET sin limit, sirvo la página HTML
    return render_template('t_restaurantes/limit_restaurantes.html')

# — Skip —
@app.route('/restaurantes/consultas_r/consul-documentos_r/skip_r', methods=['GET', 'POST'])
def skip_restaurante():
    if request.method == 'POST' or 'skip' in request.args:
        resultado = get_restaurantes_skip_servicio()
        return jsonify(resultado)
    # Si es GET sin skips, sirvo la página HTML
    return render_template('t_restaurantes/skip_restaurantes.html')


### CONSULTAS POR AGREGACION
@app.route('/restaurantes/consultas_r/consul-agregacion_r')
def consultas_agregacion_restaurantes():
    return render_template('t_restaurantes/consultas_agregacion_restaurantes.html')

### simples
@app.route('/restaurantes/consultas_r/consul-agregacion_r/simple_r')
def agregacion_simple_restaurantes():
    return render_template('t_restaurantes/agregacion_simple_restaurantes.html')

# — Match —  
@app.route('/restaurantes/consultas_r/consul-agregacion_r/simple_r/match_r', methods=['GET', 'POST'])
def match_restaurante():
    if request.method == 'POST' or bool(request.args):
        resultado = get_restaurantes_match_servicio()
        return jsonify(resultado)
    return render_template('t_restaurantes/match_restaurantes.html')

# — Group —  
@app.route('/restaurantes/consultas_r/consul-agregacion_r/simple_r/group_r', methods=['GET', 'POST'])
def group_restaurante():
    if request.method == 'POST' or bool(request.args):
        resultado = get_restaurantes_group_servicio()
        return jsonify(resultado)
    return render_template('t_restaurantes/group_restaurantes.html')

# — Count — 
@app.route('/restaurantes/consultas_r/consul-agregacion_r/simple_r/count_r', methods=['GET', 'POST'])
def count_restaurante():
    # Si llega body JSON o query params no vacíos, llamamos al servicio
    if request.method == 'POST' or bool(request.args):
        # tu servicio lee request.get_json() o request.args
        resultado = get_restaurantes_count_servicio()
        return jsonify(resultado)
    return render_template('t_restaurantes/count_restaurantes.html')

# — Distinct —
@app.route('/restaurantes/consultas_r/consul-agregacion_r/simple_r/distinct_r', methods=['GET', 'POST'])
def distinct_restaurante():
    if request.method == 'POST' or bool(request.args):
        resultado = get_restaurantes_distinct_servicio()
        return jsonify(resultado)
    return render_template('t_restaurantes/distinct_restaurantes.html')

#Actualizar usuarios
@app.route('/restaurantes/actualizar_r', methods=['GET', 'PUT'])
def actualizar_restaurante():
    if request.method == 'PUT':
        data = request.get_json()  
        resultado = actualizar_restaurantes_servicio(data)
        return jsonify(resultado), 200
    return render_template('t_restaurantes/actualizar_restaurantes.html')

#Eliminar usuarios
@app.route('/restaurantes/eliminar_r', methods=['GET', 'DELETE'])
def eliminar_restaurante():
    if request.method == 'DELETE':
        data = request.get_json()              
        resultado = eliminar_restaurantes_servicio(data)
        return jsonify(resultado), 200
    return render_template('t_restaurantes/eliminar_restaurantes.html')

### agg pipeline
@app.route('/restaurante/consultas_r/consul-agregacion_r/pipeline_r', methods=['GET','POST'])
def pipeline_restaurantes():
    if request.method == 'POST':
        # No necesitas leer aquí request.get_json() ni pasarlo al servicio
        resultado = aggregation_pipeline_r_servicio()
        return jsonify(resultado), 200

    # GET: renderizamos el formulario
    return render_template('t_restaurantes/pipeline_restaurantes.html')

### arrays
@app.route('/restaurantes/consultas_r/consul-agregacion_r/arrays_r')
def agregacion_arrays_restaurantes():
    return render_template('t_restaurantes/agregacion_arrays_restaurantes.html')

# — Push —
@app.route('/restaurantes/consultas_r/consul-agregacion_r/arrays_r/push_r', methods=['GET', 'POST'])
def push_restaurante():
    if request.method == 'POST':
        resultado = push_restaurante_servicio()
        if isinstance(resultado, tuple):
            payload, code = resultado
            return jsonify(payload), code
        return jsonify(resultado), 200
    return render_template('t_restaurantes/push_restaurantes.html')

# — Pull —
@app.route('//restaurantes/consultas_r/consul-agregacion_r/arrays_r/pull_r', methods=['GET', 'POST'])
def pull_restaurante():
    if request.method == 'POST':
        resultado = pull_restaurante_servicio()
        if isinstance(resultado, tuple):
            payload, code = resultado
            return jsonify(payload), code
        return jsonify(resultado), 200
    return render_template('t_restaurantes/pull_restaurantes.html')

# — AddToSet —
@app.route('/restaurantes/consultas_r/consul-agregacion_r/arrays_r/addToSet_r', methods=['GET', 'POST'])
def add_to_set_restaurante():
    if request.method == 'POST':
        resultado = add_to_set_restaurante_servicio()
        if isinstance(resultado, tuple):
            payload, code = resultado
            return jsonify(payload), code
        return jsonify(resultado), 200
    return render_template('t_restaurantes/add_to_set_restaurantes.html')

### embedded
@app.route('/restaurante/consultas_r/consul-agregacion_r/embedded_r')
def agregacion_embedded_restaurantes():
    return render_template('t_restaurantes/agregacion_embedded_restaurantes.html')

@app.route('/restaurantes/consultas_r/consul-agregacion_r/embedded_r/project_r', methods=['GET', 'POST'])
def project_restaurantes():
    if request.method == 'POST':
        # Ejecuta el servicio y devuelve JSON
        resultado = project_restaurante_servicio()
        return jsonify(resultado)
    # Si es GET, simplemente renderiza el formulario
    return render_template('t_restaurantes/project_restaurantes.html')

@app.route('/restaurantes/consultas_r/consul-agregacion_r/embedded_r/unwind_r', methods=['GET', 'POST'])
def unwind_restaurantes():
    if request.method == 'POST':
        resultado = unwind_restaurante_servicio()
        return jsonify(resultado)
    return render_template('t_restaurantes/unwind_restaurantes.html')

@app.route('/restaurantes/consultas_r/consul-agregacion_r/embedded_r/lookup_r', methods=['GET', 'POST'])
def lookup_restaurantes():
    if request.method == 'POST':
        resultado = lookup_restaurante_servicio()
        return jsonify(resultado)
    return render_template('t_restaurantes/lookup_restaurantes.html')


### LANDING PAGE MENU -----------------------------------------------------------------------------------------------------

@app.route('/menu')
def home_menu():
    return render_template('t_menu/menu.html')

@app.route('/menu/crear_m', methods=['GET', 'POST'])
def crear_menu():
    if request.method == 'POST':
        data = request.get_json()         # JSON enviado desde el cliente
        resultado = crear_menu_servicio(data)
        # Puedes devolver un status code 201 si creaste con éxito
        return jsonify(resultado), 201
    return render_template('t_menu/crear_menu.html')
### CONSULTAS

@app.route('/menu/consultas_m')
def consultas_menu():
    # esta será la landing de consultas: match vs aggregation
    return render_template('t_menu/consultas_menu.html')

### CONSULTAS A DOCUMENTOS
@app.route('/menu/consultas_m/consul-documentos_m')
def consultas_documentos_menu():
    return render_template('t_menu/consultas_documentos_menu.html')

# — Filtro —
@app.route('/menu/consultas_m/consul-documentos_m/filtro_m', methods=['GET', 'POST'])
def filtro_menu():
    if request.method == 'POST':
        resultado = get_menu_filtros_servicio()
        return jsonify(resultado)
    return render_template('t_menu/filtro_menu.html')

# — Proyección —
@app.route('/menu/consultas_m/consul-documentos_m/proyeccion_m', methods=['GET', 'POST'])
def proyeccion_menu():
    if request.method == 'POST':
        resultado = get_restaurantes_proyeccion_servicio()
        return jsonify(resultado)
    return render_template('t_menu/proyeccion_menu.html')

# — Ordenamiento —
@app.route('/menu/consultas_m/consul-documentos_m/ordenamiento_m', methods=['GET', 'POST'])
def ordenamiento_menu():
    if request.method == 'POST':
        resultado = get_menu_ordenamiento_servicio()
        return jsonify(resultado)
    return render_template('t_menu/ordenamiento_menu.html')

# — Limit —
@app.route('/menu/consultas_m/consul-documentos_m/limit_m', methods=['GET', 'POST'])
def limit_menu():
    # Si es POST (desde formulario JSON) o viene el query param `limit`, devolvemos datos
    if request.method == 'POST' or 'limit' in request.args:
        resultado = get_menu_limit_servicio()
        return jsonify(resultado)
    # Si es GET sin limit, sirvo la página HTML
    return render_template('t_menu/limit_menu.html')

# — Skip —
@app.route('/menu/consultas_m/consul-documentos_m/skip_m', methods=['GET', 'POST'])
def skip_menu():
    if request.method == 'POST' or 'skip' in request.args:
        resultado = get_menu_skip_servicio()
        return jsonify(resultado)
    # Si es GET sin skips, sirvo la página HTML
    return render_template('t_menu/skip_menu.html')


### CONSULTAS POR AGREGACION
@app.route('/menu/consultas_m/consul-agregacion_m')
def consultas_agregacion_menu():
    return render_template('t_menu/consultas_agregacion_menu.html')

### simples
@app.route('/menu/consultas_m/consul-agregacion_m/simple_m')
def agregacion_simple_menu():
    return render_template('t_menu/agregacion_simple_menu.html')

# — Match —  
@app.route('/menu/consultas_m/consul-agregacion_m/simple_m/match_m', methods=['GET', 'POST'])
def match_menu():
    if request.method == 'POST' or bool(request.args):
        resultado = get_menu_match_servicio()
        return jsonify(resultado)
    return render_template('t_menu/match_menu.html')

# — Group —  
@app.route('/menu/consultas_m/consul-agregacion_m/simple_m/group_m', methods=['GET', 'POST'])
def group_menu():
    if request.method == 'POST' or bool(request.args):
        resultado = get_menu_group_servicio()
        return jsonify(resultado)
    return render_template('t_menu/group_menu.html')

# — Count — 
@app.route('/menu/consultas_m/consul-agregacion_m/simple_m/count_m', methods=['GET', 'POST'])
def count_menu():
    # Si llega body JSON o query params no vacíos, llamamos al servicio
    if request.method == 'POST' or bool(request.args):
        # tu servicio lee request.get_json() o request.args
        resultado = get_menu_count_servicio()
        return jsonify(resultado)
    return render_template('t_menu/count_menu.html')

# — Distinct —
@app.route('/menu/consultas_m/consul-agregacion_m/simple_m/distinct_m', methods=['GET', 'POST'])
def distinct_menu():
    if request.method == 'POST' or bool(request.args):
        resultado = get_menu_distinct_servicio()
        return jsonify(resultado)
    return render_template('t_menu/distinct_menu.html')


### agg pipeline
@app.route('/menu/consultas_m/consul-agregacion_m/pipeline_m', methods=['GET','POST'])
def pipeline_menu():
    if request.method == 'POST':
        # No necesitas leer aquí request.get_json() ni pasarlo al servicio
        resultado = aggregation_pipeline_menu_servicio()
        return jsonify(resultado), 200

    # GET: renderizamos el formulario
    return render_template('t_menu/pipeline_menu.html')

### arrays
@app.route('/menu/consultas_m/consul-agregacion_m/arrays_m')
def agregacion_arrays_menu():
    return render_template('t_menu/agregacion_arrays_menu.html')

# — Push —
@app.route('/menu/consultas_m/consul-agregacion_m/arrays_m/push_m', methods=['GET', 'POST'])
def push_menu():
    if request.method == 'POST':
        resultado = push_menu_servicio()
        if isinstance(resultado, tuple):
            payload, code = resultado
            return jsonify(payload), code
        return jsonify(resultado), 200
    return render_template('t_menu/push_menu.html')

# — Pull —
@app.route('//menu/consultas_m/consul-agregacion_m/arrays_m/pull_m', methods=['GET', 'POST'])
def pull_menu():
    if request.method == 'POST':
        resultado = pull_menu_servicio()
        if isinstance(resultado, tuple):
            payload, code = resultado
            return jsonify(payload), code
        return jsonify(resultado), 200
    return render_template('t_menu/pull_menu.html')

# — AddToSet —
@app.route('/menu/consultas_m/consul-agregacion_m/arrays_m/addToSet_m', methods=['GET', 'POST'])
def add_to_set_menu():
    if request.method == 'POST':
        resultado = add_to_set_menu_servicio()
        if isinstance(resultado, tuple):
            payload, code = resultado
            return jsonify(payload), code
        return jsonify(resultado), 200
    return render_template('t_menu/add_to_set_menu.html')

### embedded
@app.route('/menu/consultas_m/consul-agregacion_m/embedded_m')
def agregacion_embedded_menu():
    return render_template('t_menu/agregacion_embedded_menu.html')

@app.route('/menu/consultas_m/consul-agregacion_m/embedded_m/project_m', methods=['GET', 'POST'])
def project_menu():
    if request.method == 'POST':
        # Ejecuta el servicio y devuelve JSON
        resultado = project_menu_servicio()
        return jsonify(resultado)
    # Si es GET, simplemente renderiza el formulario
    return render_template('t_menu/project_menu.html')

@app.route('/menu/consultas_m/consul-agregacion_m/embedded_m/unwind_m', methods=['GET', 'POST'])
def unwind_menu():
    if request.method == 'POST':
        resultado = unwind_menu_servicio()
        return jsonify(resultado)
    return render_template('t_menu/unwind_menu.html')

@app.route('/menu/consultas_m/consul-agregacion_m/embedded_m/lookup_m', methods=['GET', 'POST'])
def lookup_menu():
    if request.method == 'POST':
        resultado = lookup_menu_servicio()
        return jsonify(resultado)
    return render_template('t_menu/lookup_menu.html')

#Actualizar articulo menu
@app.route('/menu/actualizar_m', methods=['GET', 'PUT'])
def actualizar_menu():
    if request.method == 'PUT':
        data = request.get_json()  
        resultado = actualizar_menu_servicio(data)
        return jsonify(resultado), 200
    return render_template('t_menu/actualizar_menu.html')

#Eliminar usuarios
@app.route('/menu/eliminar_m', methods=['GET', 'DELETE'])
def eliminar_menu():
    if request.method == 'DELETE':
        data = request.get_json()              
        resultado = eliminar_menu_servicio(data)
        return jsonify(resultado), 200
    return render_template('t_menu/eliminar_menu.html')

### LANDING PAGE PEDIDOS -----------------------------------------------------------------------------------------------------
@app.route('/pedidos')
def home_pedidos():
    return render_template('t_pedidos/pedidos.html')

### LANDING PAGE RESEÑAS -----------------------------------------------------------------------------------------------------
@app.route('/reseñas')
def home_resenas():
    return render_template('t_resenas/resenas.html')



if __name__ == "__main__":
    app.run(debug=True)