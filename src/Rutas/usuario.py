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

@usuario.route('/paginacion', methods=['GET'])
def get_usuario_skip_limit():
    return get_usuarios_skip_limit_servicio()

@usuario.route('/consulta-completa', methods=['GET'])
def get_usuario_consulta_completa():
    return get_usuarios_consulta_completa_servicio()
