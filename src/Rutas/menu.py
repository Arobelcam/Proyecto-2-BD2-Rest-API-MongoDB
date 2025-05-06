from flask import Blueprint
from services.menu import *
menu = Blueprint('menu', __name__)

@menu.route('/crear_m', methods=['POST'])
def create_menu():
    return crear_menu_servicio()

@menu.route('/actualizar_m', methods=['PUT'])
def update_menu():
    return actualizar_menu_servicio()

@menu.route('/eliminar_m', methods=['DELETE'])
def delete_menu():
    return eliminar_menu_servicio()

#Consultas a documentos
@menu.route('/filtro_m', methods=['GET'])
def get_menu_filtro():
    return get_menu_filtros_servicio()

@menu.route('/proyeccion_m', methods=['GET'])
def get_menu_proyeccion():
    return get_menu_proyeccion_servicio()

@menu.route('/ordenamiento_m', methods=['GET'])
def get_menu_ordenamiento():
    return get_menu_ordenamiento_servicio()

@menu.route('/limit_m', methods=['GET'])
def get_menu_limit():
    return get_menu_limit_servicio()

@menu.route('/skip_m', methods=['GET'])
def get_menu_skip():
    return get_menu_skip_servicio()

#Rutas para consultas de agregacion
@menu.route('/count_m', methods=['GET'])
def get_menu_count():
    return get_menu_count_servicio()

@menu.route('/distinct_m', methods=['GET'])
def get_menu_distinct():
    return get_menu_distinct_servicio()

@menu.route('/match_m', methods=['GET'])
def get_menu_match():
    return get_menu_match_servicio()

@menu.route('/group_m', methods=['GET'])
def get_menu_group():
    return get_menu_group_servicio()

#agregacion para manejo de arreglos
@menu.route('/push_m', methods=['POST'])
def post_menu_push():
    return push_menu_servicio()

@menu.route('/pull_m', methods=['POST'])
def post_menu_pull():
    return pull_menu_servicio()

@menu.route('/addToSet_m', methods=['POST'])
def post_menu_addToset():
    return add_to_set_menu_servicio()

#agregacion para manejo de embeddeds
@menu.route('/project_m', methods=['GET'])
def get_menu_project():
    return project_menu_servicio()

@menu.route('/unwind_m', methods=['GET'])
def get_usuario_unwind():
    return unwind_menu_servicio()

@menu.route('/lookup_m', methods=['GET'])
def get_menu_lookup():
    return lookup_menu_servicio()

#Agreggation pipeline menu
@menu.route('/pipeline_m', methods=['GET'])
def get_menu_pipeline():
    return aggregation_pipeline_menu_servicio()