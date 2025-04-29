from flask import Blueprint
from services.usuario import crear_usuario_servicio , get_usuario_servicio
usuario = Blueprint('usuario', __name__)

@usuario.route('/', methods=['GET'])
def get_usuario():
    return get_usuario_servicio()

@usuario.route('/<id>', methods=['GET'])
def get_usuario_by_id(id):
    return "Usuario with id"

@usuario.route('/', methods=['POST'])
def create_usuario():
    return crear_usuario_servicio()

@usuario.route('/', methods=['PUT'])
def update_usuario(id):
    return "Update usuario"

@usuario.route('/', methods=['DELETE'])
def delete_usuario(id):
    return "Delete usuario"
