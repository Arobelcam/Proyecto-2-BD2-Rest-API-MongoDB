from flask import Blueprint
from services.pedidos import *
pedidos = Blueprint('pedidos', __name__)

@pedidos.route('/crear_p', methods=['POST'])
def create_pedidos():
    return crear_pedidos_servicio()

@pedidos.route('/actualizar_p', methods=['PUT'])
def update_pedidos():
    return actualizar_pedidos_servicio()

@pedidos.route('/eliminar_p', methods=['DELETE'])
def delete_pedidos():
    return eliminar_pedidos_servicio()

#CONSULTAS
#Consultas a documentos
#Rutas para consultas
@pedidos.route('/filtro_p', methods=['GET'])
def get_pedidos_filtro():
    return get_pedidos_filtros_servicio()

@pedidos.route('/proyeccion_p', methods=['GET'])
def get_pedidos_proyeccion():
    return get_pedidos_proyeccion_servicio()

@pedidos.route('/ordenamiento_p', methods=['GET'])
def get_pedidos_ordenamiento():
    return get_pedidos_ordenamiento_servicio()

@pedidos.route('/limit_p', methods=['GET'])
def get_pedidos_limit():
    return get_pedidos_limit_servicio()

@pedidos.route('/skip_p', methods=['GET'])
def get_pedidos_skip():
    return get_pedidos_skip_servicio()

#Rutas para consultas de agregacion
@pedidos.route('/count_p', methods=['GET'])
def get_pedidos_count():
    return get_pedidos_count_servicio()

@pedidos.route('/distinct_p', methods=['GET'])
def get_pedidos_distinct():
    return get_pedidos_distinct_servicio()

@pedidos.route('/match_p', methods=['GET'])
def get_pedidos_match():
    return get_pedidos_match_servicio()

@pedidos.route('/group_p', methods=['GET'])
def get_pedidos_group():
    return get_pedidos_group_servicio()

#agregacion para manejo de arreglos
@pedidos.route('/push_p', methods=['POST'])
def post_pedidos_push():
    return push_pedido_servicio()

@pedidos.route('/pull_p', methods=['POST'])
def post_pedidos_pull():
    return pull_pedido_servicio()

@pedidos.route('/addToSet_p', methods=['POST'])
def post_pedidos_addToset():
    return add_to_set_pedido_servicio()

#agregacion para manejo de embeddeds
@pedidos.route('/lookup_p', methods=['GET'])
def get_pedidps_lookup():
    return lookup_pedidos_servicio()

#agreggation pipeline

@pedidos.route('/pipeline_p', methods=['GET'])
def get_pedidos_pipeline():
    return aggregation_pipeline_pedidos_servicio()
