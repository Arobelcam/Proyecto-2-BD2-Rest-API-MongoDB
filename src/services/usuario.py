from flask import request, Response
from bson import json_util
from bson import ObjectId

from config.mongodb import mongo


def get_usuario_servicio():
    data = mongo.db.usuarios.find()
    result = json_util.dumps(data)
    return Response(result, mimetype="application/json")

### Funcion de servicio para crear usuarios
def crear_usuarios_servicio():
    data = request.get_json()

    # Si recibes un solo usuario (diccionario), lo conviertes en lista
    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        return {"error": "El cuerpo debe ser un objeto o una lista de usuarios"}, 400

    usuarios_a_insertar = []

    for item in data:
        nombre = item.get('nombre')
        email = item.get('email')
        telefono = item.get('telefono')
        direccion = item.get('direccion', {})
        calle = direccion.get('calle')
        ciudad = direccion.get('ciudad')
        preferencias = item.get('preferencias', [])

        if not nombre or not email:
            continue  # Salta usuarios incompletos

        usuario = {
            "nombre": nombre,
            "email": email,
            "telefono": telefono,
            "direccion": {
                "calle": calle,
                "ciudad": ciudad
            },
            "preferencias": preferencias
        }
        usuarios_a_insertar.append(usuario)

    if not usuarios_a_insertar:
        return {"error": "No se encontró ningún usuario válido para insertar"}, 400

    result = mongo.db.usuarios.insert_many(usuarios_a_insertar)

    return {
        "mensaje": f"{len(result.inserted_ids)} usuario(s) insertado(s) correctamente",
        "ids": [str(_id) for _id in result.inserted_ids]
    }

## Funcion de servicio para actualizar usuarios
def actualizar_usuarios_servicio():
    data = request.get_json()

    if isinstance(data, dict):
        data = [data]  # Convertir a lista si es un solo objeto

    if not isinstance(data, list):
        return {"error": "El cuerpo debe ser un objeto o lista de usuarios"}, 400

    actualizados = 0
    ids_actualizados = []

    for item in data:
        id_usuario = item.get('id')
        if not id_usuario:
            continue

        try:
            object_id = ObjectId(id_usuario)
        except:
            continue  # Saltar ID no válido

        # Construir el diccionario con los campos a actualizar
        update_fields = {}

        for campo in ['nombre', 'email', 'telefono', 'preferencias']:
            if campo in item:
                update_fields[campo] = item[campo]

        if 'direccion' in item:
            direccion = item['direccion']
            if isinstance(direccion, dict):
                update_fields['direccion'] = {
                    'calle': direccion.get('calle'),
                    'ciudad': direccion.get('ciudad')
                }

        if not update_fields:
            continue  # No hay nada que actualizar

        result = mongo.db.usuarios.update_one(
            {"_id": object_id},
            {"$set": update_fields}
        )

        if result.modified_count > 0:
            actualizados += 1
            ids_actualizados.append(str(object_id))

    if actualizados == 0:
        return {"mensaje": "No se actualizó ningún usuario"}, 400

    return {
        "mensaje": f"{actualizados} usuario(s) actualizado(s) correctamente",
        "ids_actualizados": ids_actualizados
    }


## Funcion de servicio para eliminar usuarios
def eliminar_usuarios_servicio():
    data = request.get_json()

    if isinstance(data, dict):
        ids = [data.get('id')]
    elif isinstance(data, list):
        ids = [item.get('id') if isinstance(item, dict) else item for item in data]
    elif isinstance(data, str):
        ids = [data]
    else:
        return {"error": "Formato de entrada no válido"}, 400

    # Filtrar nulos o vacíos
    ids_limpios = [ObjectId(id) for id in ids if id]

    if not ids_limpios:
        return {"error": "No se proporcionaron IDs válidos"}, 400

    resultado = mongo.db.usuarios.delete_many({"_id": {"$in": ids_limpios}})

    return {
        "mensaje": f"{resultado.deleted_count} usuario(s) eliminado(s) correctamente",
        "ids_eliminados": [str(id) for id in ids_limpios]
    }