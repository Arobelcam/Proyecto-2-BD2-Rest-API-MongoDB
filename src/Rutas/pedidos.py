from flask import Blueprint
from services.pedidos import *
pedidos = Blueprint('pedidos', __name__)