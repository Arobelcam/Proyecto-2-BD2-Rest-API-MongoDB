from flask import Blueprint
from services.usuario import crear_usuarios_servicio , get_usuario_servicio, actualizar_usuarios_servicio,eliminar_usuarios_servicio
usuario = Blueprint('usuario', __name__)

@usuario.route('/', methods=['GET'])
def get_usuario():
    return get_usuario_servicio()

@usuario.route('/<id>', methods=['GET'])
def get_usuario_by_id(id):
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
