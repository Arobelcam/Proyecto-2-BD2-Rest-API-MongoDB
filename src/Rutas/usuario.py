from flask import Blueprint
from services.usuario import *
usuario = Blueprint('usuario', __name__)

@usuario.route('/', methods=['GET'])
def get_usuario():
    return get_usuario_servicio()

@usuario.route('/<id>', methods=['GET'])
def get_usuario_by_id():
    return "Usuario with id"

@usuario.route('/', methods=['POST'])
def create_usuarios():
    return crear_usuarios_servicio()


@usuario.route('/', methods=['PUT'])
def update_usuarios():
    return actualizar_usuarios_servicio()

@usuario.route('/', methods=['DELETE'])
def delete_usuarios():
    return eliminar_usuarios_servicio()

#Rutas para consultas
@usuario.route('/filtro', methods=['GET'])
def get_usuario_filtro():
    return get_usuarios_filtros_servicio()

@usuario.route('/proyeccion', methods=['GET'])
def get_usuario_proyeccion():
    return get_usuarios_proyeccion_servicio()

@usuario.route('/ordenamiento', methods=['GET'])
def get_usuario_ordenamiento():
    return get_usuarios_ordenamiento_servicio()

@usuario.route('/limit', methods=['GET'])
def get_usuario_limit():
    return get_usuarios_limit_servicio()

@usuario.route('/skip', methods=['GET'])
def get_usuario_skip():
    return get_usuarios_skip_servicio()

@usuario.route('/consulta-completa', methods=['GET'])
def get_usuario_consulta_completa():
    return get_usuarios_consulta_completa_servicio()

#Rutas para consultas de agregacion
@usuario.route('/count', methods=['GET'])
def get_usuario_count():
    return get_usuarios_count_servicio()

@usuario.route('/distinct', methods=['GET'])
def get_usuario_distinct():
    return get_usuarios_distinct_servicio()

@usuario.route('/match', methods=['GET'])
def get_usuario_match():
    return get_usuarios_match_servicio()

@usuario.route('/group', methods=['GET'])
def get_usuario_group():
    return get_usuarios_group_servicio()

#agregacion para manejo de arreglos
@usuario.route('/push', methods=['POST'])
def post_usuario_push():
    return push_usuario_servicio()

@usuario.route('/pull', methods=['POST'])
def post_usuario_pull():
    return pull_usuario_servicio()

@usuario.route('/addToSet', methods=['POST'])
def post_usuario_addToset():
    return add_to_set_usuario_servicio()

#agregacion para manejo de embeddes
@usuario.route('/project', methods=['GET'])
def get_usuario_project():
    return project_usuario_servicio()

@usuario.route('/unwind', methods=['GET'])
def get_usuario_unwind():
    return unwind_usuario_servicio()

@usuario.route('/lookup', methods=['GET'])
def get_usuario_lookup():
    return lookup_usuario_servicio()

#agreggation pipeline

@usuario.route('/pipeline', methods=['GET'])
def get_usuario_pipeline():
    return aggregation_pipeline_servicio()