from flask import Blueprint
from services.reseñas import *
reseñas = Blueprint('reseñas', __name__)

@reseñas.route('/crear_re', methods=['POST'])
def create_reseñas():
    return crear_reseñas_servicio()

@reseñas.route('/actualizar_re', methods=['PUT'])
def update_reseñas():
    return actualizar_reseñas_servicio()

@reseñas.route('/eliminar_re', methods=['DELETE'])
def delete_reseñas():
    return eliminar_reseñas_servicio()

#Rutas para consultas
@reseñas.route('/filtro_re', methods=['GET'])
def get_reseñas_filtro():
    return get_reseñas_filtros_servicio()

@reseñas.route('/proyeccion_re', methods=['GET'])
def get_reseñas_proyeccion():
    return get_reseñas_proyeccion_servicio()

@reseñas.route('/ordenamiento_re', methods=['GET'])
def get_reseñas_ordenamiento():
    return get_reseñas_ordenamiento_servicio()

@reseñas.route('/limit_re', methods=['GET'])
def get_reseñas_limit():
    return get_reseñas_limit_servicio()

@reseñas.route('/skip_re', methods=['GET'])
def get_reseñas_skip():
    return get_reseñas_skip_servicio()

#Rutas para consultas de agregacion
@reseñas.route('/count_re', methods=['GET'])
def get_reseñas_count():
    return get_reseñas_count_servicio()

@reseñas.route('/distinct_re', methods=['GET'])
def get_reseñas_distinct():
    return get_reseñas_distinct_servicio()

@reseñas.route('/match_re', methods=['GET'])
def get_reseñas_match():
    return get_reseñas_match_servicio()

@reseñas.route('/group_re', methods=['GET'])
def get_reseñas_group():
    return get_reseñas_group_servicio()

