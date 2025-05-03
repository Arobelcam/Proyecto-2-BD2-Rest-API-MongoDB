from flask import request, Response, jsonify
from bson import json_util
from bson import ObjectId
import re
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
    
# Funcion para comprobacion de indices en coleccion de usuarios
def verificar_indice_y_consultar(filtros, orden=None):
    

    # Verificación para el índice compuesto del nombre y el telefono
    if 'nombre' in filtros and 'telefono' in filtros:
        if 'indice_nombre_telefono_compuesto' not in mongo.db.usuarios.index_information():
            return {"error": "Consulta no optimizada. Usa índices en 'nombre' y 'telefono'."}, 400

    # Verificación para el índice de email
    if 'email' in filtros:
        if 'email_1' not in mongo.db.usuarios.index_information():
            return {"error": "Consulta no optimizada. Usa el índice en 'email'."}, 400

    # Verificación para el índice de 'preferencias'
    if 'preferencias' in filtros:
        if 'preferencias_1' not in mongo.db.usuarios.index_information():
            return {"error": "Consulta no optimizada. Usa el índice en 'preferencias'."}, 400

    # Realizar la consulta con los filtros y ordenamiento si aplica
    usuarios = mongo.db.usuarios.find(filtros).sort(orden) if orden else mongo.db.usuarios.find(filtros)
    return list(usuarios)

# Funcion de servicio para consultas con filtros
def get_usuarios_filtros_servicio():
    data = request.get_json()  
    if not data:  
        data = request.args  

    filtros = {}

    if 'nombre' in data:
        filtros['nombre'] = re.compile(f"^{data['nombre']}$", re.IGNORECASE)
    
    if 'telefono' in data:
        filtros['telefono'] = data['telefono']
    
    if 'email' in data:
        filtros['email'] = data['email']
    
    if 'preferencias' in data:
        filtros['preferencias'] = data['preferencias']

    if 'direccion' in data:
        direccion_filtro = {}
        
        if 'calle' in data['direccion']:
            direccion_filtro['calle'] = re.compile(f".*{data['direccion']['calle']}.*", re.IGNORECASE)
        
        if 'ciudad' in data['direccion']:
            direccion_filtro['ciudad'] = re.compile(f".*{data['direccion']['ciudad']}.*", re.IGNORECASE)
        
        filtros['direccion'] = direccion_filtro

    
    usuarios = mongo.db.usuarios.find(filtros)
    
    # Devolvemos los resultados en formato lista
    return list(usuarios)


# Funcion de servicio para consultas con proyeccion
def get_usuarios_proyeccion_servicio():
    data = request.get_json()  
    proyeccion = {}

    if 'nombre' in data:
        proyeccion['nombre'] = 1
    if 'telefono' in data:
        proyeccion['telefono'] = 1
    if 'email' in data:
        proyeccion['email'] = 1
    if 'preferencias' in data:
        proyeccion['preferencias'] = 1

    # Ejecutar la consulta con la proyección
    resultado = mongo.db.usuarios.find({}, proyeccion)

    return list(resultado)


# Funcion de servicio para consultas con ordenamiento
def get_usuarios_ordenamiento_servicio():
    data = request.get_json()  
    print(f"Recibido: {data}")  

    filtros = {}
    orden = []

    if 'orden' in data:
        for orden_param in data['orden']:
            campo, direccion = orden_param
            orden.append((campo, direccion))  # Campo y dirección para el ordenamiento (1 o -1)

    if not orden:
        return {"error": "El parámetro 'orden' no puede estar vacío."}, 400

   
    resultado = mongo.db.usuarios.find(filtros).sort(orden)
    return list(resultado)


# Funcion de servicio para consultas con skip y limit
from flask import request

def get_usuarios_skip_limit_servicio():
    # Obtener los parámetros de la URL
    data = request.args
    skip = int(data.get('skip', 0))  # Si no hay skip, salta 0
    limit = int(data.get('limit', 10))  # Si no hay limit, muestra 10

    filtros = {}  # Si no hay filtros, pasamos un dict vacío

    # Verificar que la consulta utilice los índices correctos
    resultado = verificar_indice_y_consultar(filtros)

    if isinstance(resultado, tuple):  # Si retorna error
        return resultado

    # Aplicar skip y limit sobre el cursor
    usuarios = resultado.skip(skip).limit(limit)

    # Convertir el cursor en una lista y devolver los resultados
    return list(usuarios)


def verificar_indice_y_consultar(filtros):
    # Verificamos si la consulta usa índices válidos
    # Comprobamos que los filtros coincidan con índices
    indices_validos = ['nombre', 'telefono', 'email', 'preferencias']

    # Validación para cada campo
    for campo in filtros.keys():
        if campo not in indices_validos:
            return {"error": f"El campo '{campo}' no es un campo indexado."}, 400

    # Si la consulta es válida, realizamos la consulta en la base de datos y devolvemos el cursor
    resultado = mongo.db.usuarios.find(filtros)

    # Asegúrate de no convertir el resultado en lista aquí, mantenlo como cursor
    return resultado


# Funcion de servicio para consulta completa
def get_usuarios_consulta_completa_servicio():
    data = request.args  # Recibe los filtros y el orden

    filtros = {}
    orden = []

    # Filtros
    if 'nombre' in data:
        filtros['nombre'] = data['nombre']
    if 'telefono' in data:
        filtros['telefono'] = data['telefono']
    if 'email' in data:
        filtros['email'] = data['email']
    if 'preferencias' in data:
        filtros['preferencias'] = data['preferencias']

    # Ordenamiento
    if 'orden' in data:
        orden.append(('nombre', 1))  # Ordenar por nombre (puedes cambiarlo)

    # Verificar que la consulta utilice los índices correctos
    resultado = verificar_indice_y_consultar(filtros, orden)

    if isinstance(resultado, tuple):  # Si retorna error
        return resultado

    skip = int(data.get('skip', 0))  # Si no hay skip, salta 0
    limit = int(data.get('limit', 10))  # Si no hay limit, muestra 10

    usuarios = resultado.skip(skip).limit(limit)
    return list(usuarios)
