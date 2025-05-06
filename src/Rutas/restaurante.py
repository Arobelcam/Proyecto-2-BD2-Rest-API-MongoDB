from flask import Blueprint
from services.restaurante import *
restaurante = Blueprint('restaurante', __name__)

@restaurante.route('/crear_r', methods=['POST'])
def crear_restaurantes():
    return crear_restaurantes_servicio()

@restaurante.route('/actualizar_r', methods=['PUT'])
def actualizar_restaurantes():
    return actualizar_restaurantes_servicio()

@restaurante.route('/eliminar_r', methods=['DELETE'])
def eliminar_restaurantes():
    return eliminar_restaurantes_servicio()

### CONSULTAS
# Consultas a documentos
@restaurante.route('/filtro_r', methods=['GET'])
def get_restaurante_filtro():
    return get_restaurantes_filtros_servicio()

@restaurante.route('/proyeccion_r', methods=['GET'])
def get_restaurante_proyeccion():
    return get_restaurantes_proyeccion_servicio()

@restaurante.route('/ordenamiento_r', methods=['GET'])
def get_restaurante_ordenamiento():
    return get_restaurantes_ordenamiento_servicio()

@restaurante.route('/limit_r', methods=['GET'])
def get_restaurante_limit():
    return get_restaurantes_limit_servicio()

@restaurante.route('/skip_r', methods=['GET'])
def get_restaurante_skip():
    return get_restaurantes_skip_servicio()

#Consultas por agregacion
#Simples
@restaurante.route('/count_r', methods=['GET'])
def get_restaurante_count():
    return get_restaurantes_count_servicio()

@restaurante.route('/distinct_r', methods=['GET'])
def get_restaurante_distinct():
    return get_restaurantes_distinct_servicio()

@restaurante.route('/match_r', methods=['GET'])
def get_restaurante_match():
    return get_restaurantes_match_servicio()

@restaurante.route('/group_r', methods=['GET'])
def get_usuario_group():
    return get_restaurantes_group_servicio()

@restaurante.route('/push_r', methods=['POST'])
def post_restaurante_push():
    return push_restaurante_servicio()

@restaurante.route('/pull_r', methods=['POST'])
def post_restaurante_pull():
    return pull_restaurante_servicio()

@restaurante.route('/addToSet_r', methods=['POST'])
def post_restaurante_addToset():
    return add_to_set_restaurante_servicio()

#agregacion para manejo de embeddeds
@restaurante.route('/project_r', methods=['GET'])
def get_restaurante_project():
    return project_restaurante_servicio()

@restaurante.route('/unwind_r', methods=['GET'])
def get_restaurante_unwind():
    return unwind_restaurante_servicio()

@restaurante.route('/lookup_r', methods=['GET'])
def get_restaurante_lookup():
    return lookup_restaurante_servicio()

#agreggation pipeline
@restaurante.route('/pipeline_r', methods=['GET'])
def get_restaurante_pipeline():
    return aggregation_pipeline_r_servicio()