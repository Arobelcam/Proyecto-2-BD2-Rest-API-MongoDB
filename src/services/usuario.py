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
            continue  

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
    data = request.get_json()  # JSON con valores 1 y/o 0
    includes = [f for f, v in data.items() if v == 1]
    excludes = [f for f, v in data.items() if v == 0]

    # Elegir modo de proyección
    if includes:
        # Modo inclusión: solo los campos marcados con 1
        projection = {field: 1 for field in includes}
    elif excludes:
        # Modo exclusión: solo los campos marcados con 0
        projection = {field: 0 for field in excludes}
    else:
        # Sin proyección explícita
        projection = {}

    # Ejecutar consulta
    resultado = mongo.db.usuarios.find({}, projection)
    return list(resultado)



# Funcion de servicio para consultas con ordenamiento
def get_usuarios_ordenamiento_servicio():
    data = request.get_json()
    campo = data.get('campo')
    orden = data.get('orden')

    # Validaciones
    if not campo or orden not in (1, -1):
        return {"error": "Debes enviar 'campo' (nombre, email, telefono) y 'orden' (1 o -1)."}, 400

    # Campos permitidos para ordenar
    campos_validos = ['nombre', 'email', 'telefono']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido para ordenamiento."}, 400

    try:
        # Ejecutar la consulta con ordenamiento
        cursor = mongo.db.usuarios.find({}).sort(campo, orden)
        return list(cursor)
    except Exception as e:
        return {"error": f"Ocurrió un error al ordenar: {str(e)}"}, 500



# Funcion de servicio para consultas con limit

def get_usuarios_limit_servicio():
    data = request.args
    limit = int(data.get('limit', 10))  

    filtros = {}  

    resultado = verificar_indice_y_consultar(filtros)

    if isinstance(resultado, tuple): 
        return resultado

    # Aplicar limit sobre el cursor
    usuarios = resultado.limit(limit)

    return list(usuarios)

def get_usuarios_skip_servicio():
    data = request.args
    skip = int(data.get('skip', 0))  

    filtros = {}  # Si no hay filtros, pasamos un dict vacío

    resultado = verificar_indice_y_consultar(filtros)

    if isinstance(resultado, tuple):  # Si retorna error
        return resultado

    # Aplicar skip sobre el cursor
    usuarios = resultado.skip(skip)

    return list(usuarios)


def verificar_indice_y_consultar(filtros):
    # Verificamos si la consulta usa índices válidos
    indices_validos = ['nombre', 'telefono', 'email', 'preferencias']

    for campo in filtros.keys():
        if campo not in indices_validos:
            return {"error": f"El campo '{campo}' no es un campo indexado."}, 400

    # Si la consulta es válida, realizamos la consulta en la base de datos y devolvemos el cursor
    resultado = mongo.db.usuarios.find(filtros)

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


###   FUCIONES DE SERVICIO DE AGREGACION

# Funcion de servicio para contar usuarios
def get_usuarios_count_servicio():
    data = request.args
    filtros = {}

    # Si el parámetro 'preferencias' está presente en la URL, lo agregamos al filtro
    if 'preferencias' in data:
        filtros['preferencias'] = data['preferencias']

    # Si el parámetro 'nombre' está presente en la URL, lo agregamos al filtro
    if 'nombre' in data:
        filtros['nombre'] = data['nombre']

    # Verificar que la consulta utilice los índices correctos
    resultado = verificar_indice_y_consultar(filtros)

    if isinstance(resultado, tuple):  # Si retorna error
        return resultado

    # Realizar la agregación de contar los documentos que cumplen con el filtro
    count = mongo.db.usuarios.count_documents(filtros)

    # Devolver el número de documentos encontrados
    return {"count": count}

# funcion de servicio para hacer distinciones
def get_usuarios_distinct_servicio():
    # Obtener los parámetros de la URL
    data = request.args
    campo = data.get('campo', '')  # El campo en el que se va a buscar los valores distintos

    if not campo:
        return {"error": "El parámetro 'campo' es obligatorio para realizar la consulta distinct."}, 400

    # Verificar que el campo sea válido
    campos_validos = ['preferencias', 'nombre', 'telefono', 'email']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido para la operación distinct."}, 400

    # Realizar la consulta de distinct en el campo especificado
    resultado = mongo.db.usuarios.distinct(campo)

    # Devolver los valores únicos encontrados
    return {campo: resultado}

# Funcion de servicio para hacer match
def get_usuarios_match_servicio():
    # Obtener los parámetros de la URL
    data = request.args
    filtros = {}

    # Si el parámetro 'preferencias' está presente en la URL, lo agregamos al filtro
    if 'preferencias' in data:
        filtros['preferencias'] = data['preferencias']

    # Si el parámetro 'nombre' está presente en la URL, lo agregamos al filtro
    if 'nombre' in data:
        filtros['nombre'] = data['nombre']

    # Si el parámetro 'telefono' está presente en la URL, lo agregamos al filtro
    if 'telefono' in data:
        filtros['telefono'] = data['telefono']

    # Si el parámetro 'email' está presente en la URL, lo agregamos al filtro
    if 'email' in data:
        filtros['email'] = data['email']

    # Crear el pipeline de agregación con el operador $match
    pipeline = [
        {"$match": filtros}  # Aplicamos el filtro usando $match
    ]
    
    # Ejecutamos el pipeline en la colección
    resultado = mongo.db.usuarios.aggregate(pipeline)

    # Convertir el cursor en una lista y devolver los resultados
    return list(resultado)

#Funcion de servicio para hacer group
def get_usuarios_group_servicio():
    # Obtener los parámetros de la URL
    data = request.args
    filtros = {}

    # Si el parámetro 'preferencias' está presente, lo agregamos al filtro
    if 'preferencias' in data:
        filtros['preferencias'] = data['preferencias']

    # Crear el pipeline de agregación con el operador $group
    pipeline = [
        {"$match": filtros},  # Primero aplicamos el filtro con $match
        {"$group": {  # Luego agrupamos los resultados
            "_id": "$preferencias",  # Agrupamos por el campo 'preferencias'
            "total_usuarios": {"$sum": 1}  # Contamos el total de usuarios por preferencia
        }}
    ]

    # Ejecutamos el pipeline en la colección
    resultado = mongo.db.usuarios.aggregate(pipeline)

    # Convertir el cursor en una lista y devolver los resultados
    return list(resultado)

# Funcion de servicio para hacer push
def push_usuario_servicio():
    # Obtener los parámetros de la URL
    data = request.get_json()  # Obtener datos del cuerpo de la solicitud
    usuario_id = data.get('usuario_id')  # El ID del usuario de donde se agregará el valor
    campo = data.get('campo')  # El campo del array al que se agregará el valor
    valor = data.get('valor')  # El valor que se agregará al array

    if not usuario_id or not campo or not valor:
        return {"error": "Faltan parámetros 'usuario_id', 'campo' o 'valor'"}, 400

    # Convertir el usuario_id a ObjectId de MongoDB si es necesario
    try:
        usuario_id = ObjectId(usuario_id)
    except Exception as e:
        return {"error": f"El ID de usuario no es válido: {str(e)}"}, 400

    # Validar que el campo sea uno de los esperados
    campos_validos = ['nombre', 'telefono', 'email', 'preferencias', 'direccion']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido."}, 400

    # Verificar si el campo es "preferencias" o no es un arreglo
    if campo != 'preferencias':
        usuario = mongo.db.usuarios.find_one({"_id": usuario_id})
        if not isinstance(usuario.get(campo), list):
            return {"error": f"El campo '{campo}' no es un arreglo. No se puede usar el operador $push."}, 400

    # Realizar la operación $push para agregar el valor al array del campo correspondiente
    resultado = mongo.db.usuarios.update_one(
        {"_id": usuario_id},  # Filtro para el usuario por ID
        {"$push": {campo: valor}}  # Agregar el valor al array del campo
    )

    # Verificar si se modificó el documento
    if resultado.matched_count > 0:
        return {"message": f"{valor} agregado exitosamente a {campo}."}
    else:
        return {"error": "Usuario no encontrado."}, 404

#Funcion de servicio para hacer pull
def pull_usuario_servicio():
    # Obtener los parámetros de la URL
    data = request.get_json()  # Obtener datos del cuerpo de la solicitud
    usuario_id = data.get('usuario_id')  # El ID del usuario
    campo = data.get('campo')  # El campo del array del que se eliminará el valor
    valor = data.get('valor')  # El valor que se eliminará del array

    if not usuario_id or not campo or not valor:
        return {"error": "Faltan parámetros 'usuario_id', 'campo' o 'valor'"}, 400

    # Convertir el usuario_id a ObjectId de MongoDB si es necesario
    try:
        usuario_id = ObjectId(usuario_id)
    except Exception as e:
        return {"error": f"El ID de usuario no es válido: {str(e)}"}, 400

    # Validar que el campo sea uno de los esperados
    campos_validos = ['nombre', 'telefono', 'email', 'preferencias', 'direccion']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido."}, 400

    # Verificar si el campo es "preferencias" o no es un arreglo
    if campo != 'preferencias':
        usuario = mongo.db.usuarios.find_one({"_id": usuario_id})
        if not isinstance(usuario.get(campo), list):
            return {"error": f"El campo '{campo}' no es un arreglo. No se puede usar el operador $pull."}, 400

    # Realizar la operación $pull para eliminar el valor del array del campo correspondiente
    resultado = mongo.db.usuarios.update_one(
        {"_id": usuario_id},  # Filtro para el usuario por ID
        {"$pull": {campo: valor}}  # Eliminar el valor del array del campo
    )

    # Verificar si se modificó el documento
    if resultado.matched_count > 0:
        return {"message": f"{valor} eliminado exitosamente de {campo}."}
    else:
        return {"error": "Usuario no encontrado."}, 404


#Funcion de servicio para hacer uso de AddToSet
def add_to_set_usuario_servicio():
    # Obtener los parámetros de la URL
    data = request.get_json()  # Obtener datos del cuerpo de la solicitud
    usuario_id = data.get('usuario_id')  # El ID del usuario
    campo = data.get('campo')  # El campo del array al que se agregará el valor
    valor = data.get('valor')  # El valor que se agregará al array

    if not usuario_id or not campo or not valor:
        return {"error": "Faltan parámetros 'usuario_id', 'campo' o 'valor'"}, 400

    # Convertir el usuario_id a ObjectId de MongoDB si es necesario
    try:
        usuario_id = ObjectId(usuario_id)
    except Exception as e:
        return {"error": f"El ID de usuario no es válido: {str(e)}"}, 400

    # Validar que el campo sea uno de los esperados
    campos_validos = ['nombre', 'telefono', 'email', 'preferencias', 'direccion']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido."}, 400

    # Verificar si el campo es "preferencias" o no es un arreglo
    if campo != 'preferencias':
        usuario = mongo.db.usuarios.find_one({"_id": usuario_id})
        if not isinstance(usuario.get(campo), list):
            return {"error": f"El campo '{campo}' no es un arreglo. No se puede usar el operador $addToSet."}, 400

    # Verificar si el valor ya existe en el array para evitar duplicados
    usuario = mongo.db.usuarios.find_one({"_id": usuario_id})
    if usuario and valor in usuario.get(campo, []):
        return {"message": f"El valor '{valor}' ya está presente en el campo '{campo}', no se agregó."}

    # Realizar la operación $addToSet para agregar el valor al array del campo correspondiente
    resultado = mongo.db.usuarios.update_one(
        {"_id": usuario_id},  # Filtro para el usuario por ID
        {"$addToSet": {campo: valor}}  # Agregar el valor al array del campo
    )

    # Verificar si se modificó el documento
    if resultado.matched_count > 0:
        return {"message": f"{valor} agregado exitosamente a {campo}."}
    else:
        return {"error": "Usuario no encontrado."}, 404

### FUNCIONES DE SERVICIO PARA MANEJO DE DOCUMENTOS EMBEDDED
#Funcion de servicio para hacer project
def project_usuario_servicio():
    # Obtener los parámetros de la URL
    data = request.get_json()  # Obtener datos del cuerpo de la solicitud
    usuario_id = data.get('usuario_id')  # El ID del usuario
    campos_proyectados = data.get('campos')  # Los campos a proyectar (como una lista de cadenas)

    if not usuario_id or not campos_proyectados:
        return {"error": "Faltan parámetros 'usuario_id' o 'campos'"}, 400

    # Convertir el usuario_id a ObjectId de MongoDB si es necesario
    try:
        usuario_id = ObjectId(usuario_id)
    except Exception as e:
        return {"error": f"El ID de usuario no es válido: {str(e)}"}, 400

    # Realizar la operación $project para seleccionar los campos deseados
    try:
        # Creamos un diccionario con los campos a proyectar
        campos_dict = {campo: 1 for campo in campos_proyectados}  # Todos los campos seleccionados se proyectan con valor 1

        # Realizar la consulta con $project
        usuario = mongo.db.usuarios.find_one({"_id": usuario_id}, campos_dict)

        if usuario:
            return {"usuario": usuario}
        else:
            return {"error": "Usuario no encontrado."}, 404
    except Exception as e:
        return {"error": f"Error al realizar la proyección: {str(e)}"}, 500

#Funcion de servicio para hacer unwind
def unwind_usuario_servicio():
    # Obtener los parámetros de la URL
    data = request.get_json()  # Obtener datos del cuerpo de la solicitud
    usuario_id = data.get('usuario_id')  # El ID del usuario
    campo = data.get('campo')  # El campo de arreglo que se va a descomponer

    if not usuario_id or not campo:
        return {"error": "Faltan parámetros 'usuario_id' o 'campo'"}, 400

    # Convertir el usuario_id a ObjectId de MongoDB si es necesario
    try:
        usuario_id = ObjectId(usuario_id)
    except Exception as e:
        return {"error": f"El ID de usuario no es válido: {str(e)}"}, 400

    # Validar que el campo sea un arreglo
    campos_validos = ['preferencias']  # Se espera que el campo sea "preferencias" o cualquier otro arreglo definido
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido para la operación de unwind."}, 400

    # Realizar la operación $unwind para descomponer el arreglo
    try:
        # Realizar la consulta con $unwind
        pipeline = [
            {"$match": {"_id": usuario_id}},  # Filtramos el documento por ID
            {"$unwind": f"${campo}"}  # Aplicamos el unwind al campo específico
        ]
        
        resultado = list(mongo.db.usuarios.aggregate(pipeline))  # Ejecutamos la agregación

        if resultado:
            return {"usuario_descompuesto": resultado}
        else:
            return {"error": "Usuario no encontrado."}, 404
    except Exception as e:
        return {"error": f"Error al realizar el unwind: {str(e)}"}, 500
    
#Funcion de servicio para hacer lookup
from bson import ObjectId  # Importar ObjectId desde bson

def lookup_usuario_servicio():
    # Obtener los parámetros de la solicitud
    data = request.get_json()  # Obtener datos del cuerpo de la solicitud
    usuario_id = data.get('usuario_id')  # El ID del usuario para hacer el lookup
    coleccion_lookup = data.get('coleccion_lookup')  # El nombre de la colección con la que hacer el join
    campo_local = data.get('campo_local')  # El campo en la colección actual para hacer el join
    campo_foreign = data.get('campo_foreign')  # El campo en la colección de lookup para hacer el join

    # Validar que todos los parámetros estén presentes
    if not usuario_id or not coleccion_lookup or not campo_local or not campo_foreign:
        return {"error": "Faltan parámetros 'usuario_id', 'coleccion_lookup', 'campo_local' o 'campo_foreign'"}, 400

    # Convertir el usuario_id a ObjectId de MongoDB
    try:
        usuario_id = ObjectId(usuario_id)  # Intentamos convertir a ObjectId
    except Exception as e:
        return {"error": f"El ID de usuario no es válido: {str(e)}"}, 400

    # Realizar la operación de agregación con $lookup
    try:
        pipeline = [
            {
                "$lookup": {
                    "from": coleccion_lookup,  # Colección con la que se hace el join
                    "localField": campo_local,  # Campo de la colección actual
                    "foreignField": campo_foreign,  # Campo de la colección a buscar
                    "as": "informacion_combinada"  # Nombre del campo donde se guardarán los resultados
                }
            },
            {
                "$match": {"_id": usuario_id}  # Filtrar por el usuario_id convertido a ObjectId
            },
            {
                "$project": {
                    "nombre": 1,                # Mostrar el nombre del usuario
                    "email": 1,                 # Mostrar el email del usuario
                    "informacion_combinada": 1  # Mostrar los documentos combinados de pedidos
                }
            }
        ]

        # Ejecutar la agregación
        resultado = list(mongo.db.usuarios.aggregate(pipeline))  # Ejecutar la pipeline de agregación

        if resultado:
            return {"usuario_con_info": resultado}
        else:
            return {"error": "Usuario no encontrado."}, 404
    except Exception as e:
        return {"error": f"Error al realizar el lookup: {str(e)}"}, 500

#Funcion de servicio de agreggation pipeline basado en las preferencias de comdia del usuario
def aggregation_pipeline_servicio():
    # Obtener los parámetros de la solicitud
    data = request.get_json()
    preferencias = data.get('preferencias')    # Preferencias a filtrar (por ejemplo: ["comida", "deportes"])
    sort_order = data.get('sort_order', -1)  # Orden (1 para ascendente, -1 para descendente)
    limit = data.get('limit', 5)  # Limite de resultados

    # Validaciones de entrada
    if not preferencias:
        return {"error": "El campo 'preferencias' es requerido."}, 400
    if not isinstance(preferencias, list):
        return {"error": "'preferencias' debe ser una lista."}, 400
    if not isinstance(sort_order, int) or sort_order not in [-1, 1]:
        return {"error": "'sort_order' debe ser 1 (ascendente) o -1 (descendente)."}, 400
    if not isinstance(limit, int) or limit <= 0:
        return {"error": "'limit' debe ser un número entero mayor a 0."}, 400

    try:
        # Construir la pipeline de agregación
        pipeline = [
            # Filtrar usuarios por las preferencias seleccionadas
            { "$match": { "preferencias": { "$in": preferencias } } },
            
            # Agrupar por preferencias y contar los usuarios
            { "$group": { "_id": "$preferencias", "total_usuarios": { "$sum": 1 } } },
            
            # Proyectar las preferencias y el total de usuarios
            { "$project": { "_id": 1, "total_usuarios": 1 } },
            
            # Ordenar por la cantidad de usuarios (total_usuarios) en el orden especificado
            { "$sort": { "total_usuarios": sort_order } },
            
            # Limitar los resultados según el parámetro 'limit'
            { "$limit": limit }
        ]

        # Ejecutar la agregación en la colección 'usuarios'
        resultado = list(mongo.db.usuarios.aggregate(pipeline))

        if resultado:
            return {"resultado": resultado}
        else:
            return {"error": "No se encontraron resultados para los criterios especificados."}, 404
    
    except Exception as e:
        return {"error": f"Error al ejecutar la pipeline: {str(e)}"}, 500
