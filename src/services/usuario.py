from flask import request, Response
from bson import json_util
from config.mongodb import mongo

def crear_usuario_servicio():
   
    data = request.get_json()
    nombre = data.get('nombre', None)
    email = data.get('email', None)
    telefono = data.get('telefono', None)
    direccion = data.get('direccion', None)
    if nombre:
        response = mongo.db.usuarios.insert_one({
            "nombre": nombre,
            "email": email,
            "telefono": telefono,
            "direccion": direccion,
            "done": False
        })
        result = {
            "id": str(response.inserted_id),
            "nombre": nombre,
            "email": email,
            "telefono": telefono,
            "direccion": direccion,
            "done": False
        }
        return result
    else:
        return  "error de carga", 400
       
def get_usuario_servicio():
    data = mongo.db.usuarios.find()
    result = json_util.dumps(data)
    return Response(result, mimetype="application/json")

    