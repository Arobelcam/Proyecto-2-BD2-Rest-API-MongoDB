from flask import request, Response, jsonify
from bson import json_util
from bson import ObjectId
import re
from config.mongodb import mongo

#Funcion de servicio para crear articulo menu
def crear_menu_servicio():
    data = request.get_json()

    # Si recibes un solo plato (diccionario), lo conviertes en lista
    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        return {"error": "El cuerpo debe ser un objeto o una lista de platos de menú"}, 400

    platos_a_insertar = []

    for item in data:
        IdRestaurante = item.get('IdRestaurante')
        nombre_plato = item.get('nombre_plato')
        precio = item.get('precio')
        categoria = item.get('categoria')
        descripcion = item.get('descripcion', '')
        ingredientes = item.get('ingredientes', [])

        if not IdRestaurante or not nombre_plato or not precio or not categoria:
            continue  # Salta los platos incompletos

        plato = {
            "IdRestaurante": ObjectId(IdRestaurante),
            "nombre_plato": nombre_plato,
            "precio": precio,
            "categoria": categoria,
            "descripcion": descripcion,
            "ingredientes": ingredientes
        }
        platos_a_insertar.append(plato)

    if not platos_a_insertar:
        return {"error": "No se encontró ningún plato válido para insertar"}, 400

    result = mongo.db.menu.insert_many(platos_a_insertar)

    return {
        "mensaje": f"{len(result.inserted_ids)} plato(s) insertado(s) correctamente",
        "ids": [str(_id) for _id in result.inserted_ids]
    }

#Funcion de servicio actualizar articulo del menu
def actualizar_menu_servicio():
    data = request.get_json()

    if isinstance(data, dict):
        data = [data]  # Convertir a lista si es un solo objeto

    if not isinstance(data, list):
        return {"error": "El cuerpo debe ser un objeto o lista de platos de menú"}, 400

    actualizados = 0
    ids_actualizados = []

    for item in data:
        id_plato = item.get('id')
        if not id_plato:
            continue

        try:
            object_id = ObjectId(id_plato)
        except:
            continue  

        update_fields = {}

        for campo in ['nombre_plato', 'precio', 'categoria', 'descripcion', 'ingredientes']:
            if campo in item:
                update_fields[campo] = item[campo]

        if not update_fields:
            continue  # No hay nada que actualizar

        result = mongo.db.menu.update_one(
            {"_id": object_id},
            {"$set": update_fields}
        )

        if result.modified_count > 0:
            actualizados += 1
            ids_actualizados.append(str(object_id))

    if actualizados == 0:
        return {"mensaje": "No se actualizó ningún plato"}, 400

    return {
        "mensaje": f"{actualizados} plato(s) actualizado(s) correctamente",
        "ids_actualizados": ids_actualizados
    }



#Funcion de servicio para eliminar articulo del menu
def eliminar_menu_servicio():
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

    resultado = mongo.db.menu.delete_many({"_id": {"$in": ids_limpios}})

    return {
        "mensaje": f"{resultado.deleted_count} plato(s) eliminado(s) correctamente",
        "ids_eliminados": [str(id) for id in ids_limpios]
    }

### CONSULTAS
# Consultas a documentos

#Funcion de servicio para filtro 
def get_menu_filtros_servicio():
    data = request.args  # Obtener parámetros de la URL
    filtros = {}

    # Filtro por nombre del plato (exacto)
    if 'nombre_plato' in data:
        filtros['nombre_plato'] = re.compile(f"^{data['nombre_plato']}$", re.IGNORECASE)
    
    # Filtro por categoría (puede contener parte de la categoría, no necesariamente exacto)
    if 'categoria' in data:
        filtros['categoria'] = re.compile(f".*{data['categoria']}.*", re.IGNORECASE)
    
    # Filtro por precio (como número)
    if 'precio' in data:
        try:
            filtros['precio'] = float(data['precio'])
        except ValueError:
            return {"error": "'precio' debe ser un número."}, 400
    
    # Filtro por descripción (busca si la descripción contiene el término proporcionado)
    if 'descripcion' in data:
        filtros['descripcion'] = re.compile(f".*{data['descripcion']}.*", re.IGNORECASE)
    
    # Filtro por ingredientes (busca aquellos que contienen un ingrediente específico)
    if 'ingredientes' in data:
        ingredientes_filtro = data['ingredientes'].split(',')
        filtros['ingredientes'] = {"$in": [ingrediente.strip() for ingrediente in ingredientes_filtro]}
    
    # Realizar la consulta en la colección 'menu'
    try:
        resultado = mongo.db.menu.find(filtros)
        return list(resultado)
    except Exception as e:
        return {"error": f"Error al realizar la consulta: {str(e)}"}, 500


#Funcion de servicio proyeccion
def get_menu_proyeccion_servicio():
    data = request.get_json()  # Obtener datos del cuerpo de la solicitud
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

    # Ejecutar consulta con la proyección en el menu
    resultado = mongo.db.menu.find({}, projection)
    return list(resultado)

#Funcion de servicio ordenamiento
def get_menu_ordenamiento_servicio():
    data = request.get_json()  # Obtener los datos de la solicitud
    campo = data.get('campo')
    orden = data.get('orden')

    # Validaciones
    if not campo or orden not in (1, -1):
        return {"error": "Debes enviar 'campo' (nombre_plato, precio, categoria) y 'orden' (1 o -1)."}, 400

    # Campos permitidos para ordenar
    campos_validos = ['nombre_plato', 'precio', 'categoria']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido para ordenamiento."}, 400

    try:
        # Ejecutar la consulta con ordenamiento
        cursor = mongo.db.menu.find({}).sort(campo, orden)
        return list(cursor)
    except Exception as e:
        return {"error": f"Ocurrió un error al ordenar: {str(e)}"}, 500

#Funcion de servicio para limit
def get_menu_limit_servicio():
    data = request.args  # Obtener parámetros de la URL
    limit = int(data.get('limit', 10))  # Por defecto limitamos a 10 resultados

    filtros = {}

    # Realizar la consulta en la colección 'menu' con el límite especificado
    try:
        resultado = mongo.db.menu.find(filtros).limit(limit)  # Aplicar el límite a la consulta
        return list(resultado)
    except Exception as e:
        return {"error": f"Error al realizar la consulta con limit: {str(e)}"}, 500

#Funcion de servicio para skip
def get_menu_skip_servicio():
    data = request.args  # Obtener parámetros de la URL
    skip = int(data.get('skip', 0))  # Por defecto comenzamos desde el primer resultado

    filtros = {}

    # Realizar la consulta en la colección 'menu' con el skip especificado
    try:
        resultado = mongo.db.menu.find(filtros).skip(skip)  # Aplicar el skip a la consulta
        return list(resultado)
    except Exception as e:
        return {"error": f"Error al realizar la consulta con skip: {str(e)}"}, 500

#Consultas por agregacion
#Simples
#Funcion de servicio para count
def get_menu_count_servicio():
    data = request.args  # Obtener parámetros de la URL
    filtros = {}

    # Filtros por los campos disponibles, puedes añadir más filtros según lo que necesites
    if 'nombre_plato' in data:
        filtros['nombre_plato'] = re.compile(f"^{data['nombre_plato']}$", re.IGNORECASE)

    if 'categoria' in data:
        filtros['categoria'] = re.compile(f".*{data['categoria']}.*", re.IGNORECASE)

    if 'precio' in data:
        try:
            filtros['precio'] = float(data['precio'])
        except ValueError:
            return {"error": "'precio' debe ser un número."}, 400

    if 'descripcion' in data:
        filtros['descripcion'] = re.compile(f".*{data['descripcion']}.*", re.IGNORECASE)

    if 'ingredientes' in data:
        ingredientes_filtro = data['ingredientes'].split(',')
        filtros['ingredientes'] = {"$in": [ingrediente.strip() for ingrediente in ingredientes_filtro]}

    # Realizar la consulta para contar los documentos
    try:
        count = mongo.db.menu.count_documents(filtros)
        return {"count": count}
    except Exception as e:
        return {"error": f"Error al realizar el conteo: {str(e)}"}, 500
    
#Funcion de servicio para distinct
def get_menu_distinct_servicio():
    # Obtener los parámetros de la URL
    data = request.args  # Obtener datos de la solicitud
    campo = data.get('campo', '')  # El campo en el que se va a buscar los valores distintos

    if not campo:
        return {"error": "El parámetro 'campo' es obligatorio para realizar la consulta distinct."}, 400

    # Verificar que el campo sea válido
    campos_validos = ['nombre_plato', 'categoria', 'precio', 'ingredientes']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido para la operación distinct."}, 400

    # Realizar la consulta de distinct en el campo especificado
    try:
        resultado = mongo.db.menu.distinct(campo)

        # Devolver los valores únicos encontrados
        return {campo: resultado}
    except Exception as e:
        return {"error": f"Error al realizar la operación distinct: {str(e)}"}, 500

#Funcion de servicio para match
def get_menu_match_servicio():
    # Obtener los parámetros de la URL
    data = request.args
    filtros = {}

    # Filtros por los campos disponibles
    if 'nombre_plato' in data:
        filtros['nombre_plato'] = re.compile(f"^{data['nombre_plato']}$", re.IGNORECASE)

    if 'categoria' in data:
        filtros['categoria'] = re.compile(f".*{data['categoria']}.*", re.IGNORECASE)

    if 'precio' in data:
        try:
            filtros['precio'] = float(data['precio'])
        except ValueError:
            return {"error": "'precio' debe ser un número."}, 400

    if 'descripcion' in data:
        filtros['descripcion'] = re.compile(f".*{data['descripcion']}.*", re.IGNORECASE)

    if 'ingredientes' in data:
        ingredientes_filtro = data['ingredientes'].split(',')
        filtros['ingredientes'] = {"$in": [ingrediente.strip() for ingrediente in ingredientes_filtro]}

    # Realizar la consulta con el filtro $match
    try:
        resultado = mongo.db.menu.find(filtros)
        return list(resultado)
    except Exception as e:
        return {"error": f"Error al realizar la consulta con match: {str(e)}"}, 500


#Funcion de servicio para group
def get_menu_group_servicio():
    # Obtener los parámetros de la URL
    data = request.args
    filtros = {}

    # Filtros por los campos disponibles
    if 'categoria' in data:
        filtros['categoria'] = re.compile(f".*{data['categoria']}.*", re.IGNORECASE)

    # Crear el pipeline de agregación con el operador $match
    pipeline = [
        {"$match": filtros},  # Primero aplicamos el filtro con $match
        {"$group": {  # Luego agrupamos los resultados
            "_id": "$categoria",  # Agrupamos por el campo 'categoria'
            "total_platos": {"$sum": 1},  # Contamos el total de platos por categoría
            "precio_promedio": {"$avg": "$precio"}  # Calculamos el precio promedio de los platos por categoría
        }}
    ]

    # Ejecutar la agregación
    try:
        resultado = list(mongo.db.menu.aggregate(pipeline))
        return resultado
    except Exception as e:
        return {"error": f"Error al realizar la agregación con group: {str(e)}"}, 500

#Consulta por agregacion manejo de arrays
#Funciond de servicio push
def push_menu_servicio():
    # Obtener los parámetros de la solicitud
    data = request.get_json()  # Obtener los datos del cuerpo de la solicitud
    menu_id = data.get('menu_id')  # El ID del plato de menú
    campo = data.get('campo')  # El campo del array al que se agregará el valor
    valor = data.get('valor')  # El valor que se agregará al array

    if not menu_id or not campo or not valor:
        return {"error": "Faltan parámetros 'menu_id', 'campo' o 'valor'"}, 400

    # Convertir el menu_id a ObjectId de MongoDB si es necesario
    try:
        menu_id = ObjectId(menu_id)
    except Exception as e:
        return {"error": f"El ID del menú no es válido: {str(e)}"}, 400

    # Validar que el campo sea uno de los esperados
    campos_validos = ['ingredientes']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido."}, 400

    # Verificar si el valor ya existe en el array para evitar duplicados
    menu = mongo.db.menu.find_one({"_id": menu_id})
    if menu and valor in menu.get(campo, []):
        return {"message": f"El valor '{valor}' ya está presente en el campo '{campo}', no se agregó."}

    # Realizar la operación $push para agregar el valor al array del campo correspondiente
    resultado = mongo.db.menu.update_one(
        {"_id": menu_id},  # Filtro para el plato de menú por ID
        {"$push": {campo: valor}}  # Agregar el valor al array del campo
    )

    # Verificar si se modificó el documento
    if resultado.matched_count > 0:
        return {"message": f"{valor} agregado exitosamente a {campo}."}
    else:
        return {"error": "Plato de menú no encontrado."}, 404
    
#Funcion de servicio pull
def pull_menu_servicio():
    # Obtener los parámetros de la solicitud
    data = request.get_json()  # Obtener los datos del cuerpo de la solicitud
    menu_id = data.get('menu_id')  # El ID del plato de menú
    campo = data.get('campo')  # El campo del array del que se eliminará el valor
    valor = data.get('valor')  # El valor que se eliminará del array

    if not menu_id or not campo or not valor:
        return {"error": "Faltan parámetros 'menu_id', 'campo' o 'valor'"}, 400

    # Convertir el menu_id a ObjectId de MongoDB si es necesario
    try:
        menu_id = ObjectId(menu_id)
    except Exception as e:
        return {"error": f"El ID del menú no es válido: {str(e)}"}, 400

    # Validar que el campo sea uno de los esperados
    campos_validos = ['ingredientes']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido."}, 400

    # Realizar la operación $pull para eliminar el valor del array del campo correspondiente
    resultado = mongo.db.menu.update_one(
        {"_id": menu_id},  # Filtro para el plato de menú por ID
        {"$pull": {campo: valor}}  # Eliminar el valor del array del campo
    )

    # Verificar si se modificó el documento
    if resultado.matched_count > 0:
        return {"message": f"{valor} eliminado exitosamente de {campo}."}
    else:
        return {"error": "Plato de menú no encontrado."}, 404


#Funcion de servicio addToSet
def add_to_set_menu_servicio():
    # Obtener los parámetros de la solicitud
    data = request.get_json()
    menu_id = data.get('menu_id')    # El ID del plato de menú
    campo = data.get('campo')        # El campo del array al que se agregará el valor
    valor = data.get('valor')        # El valor que se agregará al array

    # Validación de parámetros
    if not menu_id or not campo or not valor:
        return {"error": "Faltan parámetros 'menu_id', 'campo' o 'valor'."}, 400

    # Convertir el menu_id a ObjectId
    try:
        menu_id = ObjectId(menu_id)
    except Exception as e:
        return {"error": f"El ID del menú no es válido: {str(e)}"}, 400

    # Solo permitimos operar sobre el campo 'ingredientes'
    if campo != 'ingredientes':
        return {"error": f"El campo '{campo}' no es válido para addToSet."}, 400

    # Buscar el documento antes de intentar agregar
    menu_doc = mongo.db.menu.find_one({"_id": menu_id})
    if not menu_doc:
        return {"error": "Plato de menú no encontrado."}, 404

    # Si el valor ya existe en el array, devolvemos mensaje específico
    if valor in menu_doc.get(campo, []):
        return {"message": f"El valor '{valor}' ya existe en '{campo}', no se agregó."}

    # Si no existe, usamos $addToSet para agregar
    resultado = mongo.db.menu.update_one(
        {"_id": menu_id},
        {"$addToSet": {campo: valor}}
    )

    if resultado.modified_count > 0:
        return {"message": f"{valor} agregado exitosamente a '{campo}'."}
    else:
        return {"error": "No se pudo agregar el valor."}, 500

# Consultas por agregacion manejo de embeddes
#Funcion de servicio de project
def project_menu_servicio():
    data = request.get_json()
    menu_id = data.get('menu_id')
    campos = data.get('campos')  # lista de campos a proyectar

    if not menu_id or not campos:
        return {"error": "Faltan parámetros 'menu_id' o 'campos'."}, 400

    try:
        menu_id = ObjectId(menu_id)
    except Exception as e:
        return {"error": f"El ID del menú no es válido: {str(e)}"}, 400

    # Construir el dict de proyección
    proj = {campo: 1 for campo in campos}

    # Ejecutar la consulta con proyección
    menu = mongo.db.menu.find_one({"_id": menu_id}, proj)
    if not menu:
        return {"error": "Plato de menú no encontrado."}, 404

    return {"menu": menu}

#Funcion de servicio de unwind
def unwind_menu_servicio():
    data = request.get_json()
    menu_id = data.get('menu_id')
    campo = data.get('campo')  # debe ser 'ingredientes'

    if not menu_id or not campo:
        return {"error": "Faltan parámetros 'menu_id' o 'campo'."}, 400

    try:
        menu_id = ObjectId(menu_id)
    except Exception as e:
        return {"error": f"El ID del menú no es válido: {str(e)}"}, 400

    if campo != 'ingredientes':
        return {"error": f"El campo '{campo}' no es válido para unwind."}, 400

    pipeline = [
        {"$match": {"_id": menu_id}},
        {"$unwind": f"${campo}"}
    ]
    resultado = list(mongo.db.menu.aggregate(pipeline))
    if not resultado:
        return {"error": "Plato de menú no encontrado o arreglo vacío."}, 404

    return {"ingrediente_descompuesto": resultado}

#Funcion de servicio lookup
def lookup_menu_servicio():
    data = request.get_json()
    menu_id = data.get('menu_id')
    coleccion_lookup = data.get('coleccion_lookup', 'restaurantes')
    campo_local = data.get('campo_local', 'IdRestaurante')
    campo_foreign = data.get('campo_foreign', '_id')

    # Validar parámetros
    if not menu_id:
        return {"error": "Falta el parámetro 'menu_id'."}, 400
    if not coleccion_lookup or not campo_local or not campo_foreign:
        return {"error": "Faltan parámetros para lookup."}, 400

    # Convertir menu_id a ObjectId
    try:
        menu_obj_id = ObjectId(menu_id)
    except Exception as e:
        return {"error": f"El ID del menú no es válido: {str(e)}"}, 400

    # Construir pipeline
    pipeline = [
        {"$match": {"_id": menu_obj_id}},
        {"$lookup": {
            "from": coleccion_lookup,
            "localField": campo_local,
            "foreignField": campo_foreign,
            "as": "info_restaurante"
        }},
        {"$project": {
            "nombre_plato": 1,
            "precio": 1,
            "info_restaurante": 1
        }}
    ]

    # Ejecutar agregación
    try:
        resultado = list(mongo.db.menu.aggregate(pipeline))
    except Exception as e:
        return {"error": f"Error al ejecutar lookup: {str(e)}"}, 500

    if not resultado:
        return {"error": "Plato de menú no encontrado."}, 404

    return {"menu_con_restaurante": resultado}

#Funcion de servicio agreggation pipeline para el menu
def aggregation_pipeline_menu_servicio():
    data = request.get_json()
    categorias = data.get('categorias')
    sort_order = data.get('sort_order', -1)
    limit = data.get('limit', 5)

    # Validaciones
    if not categorias or not isinstance(categorias, list):
        return {"error": "El campo 'categorias' es requerido y debe ser una lista."}, 400
    if sort_order not in (-1, 1):
        return {"error": "'sort_order' debe ser 1 o -1."}, 400
    if not isinstance(limit, int) or limit <= 0:
        return {"error": "'limit' debe ser un entero mayor que 0."}, 400

    try:
        pipeline = [
            # 1) Filtrar por categorías
            {"$match": {"categoria": {"$in": categorias}}},
            # 2) Agrupar por restaurante
            {"$group": {
                "_id": "$IdRestaurante",
                "count_platos": {"$sum": 1},
                "avg_precio":   {"$avg": "$precio"}
            }},
            # 3) Proyectar los campos de interés
            {"$project": {
                "_id": 1,
                "count_platos": 1,
                "avg_precio": 1
            }},
            # 4) Ordenar por avg_precio
            {"$sort": {"avg_precio": sort_order}},
            # 5) Limitar cantidad de resultados
            {"$limit": limit}
        ]

        raw = list(mongo.db.menu.aggregate(pipeline))
        # Convertir ObjectId a string para JSON
        resultado = []
        for doc in raw:
            resultado.append({
                "IdRestaurante": str(doc["_id"]),
                "count_platos": doc["count_platos"],
                "avg_precio": doc["avg_precio"]
            })

        if not resultado:
            return {"error": "No se encontraron resultados con esos criterios."}, 404

        return {"resultado": resultado}

    except Exception as e:
        return {"error": f"Error al ejecutar la pipeline: {str(e)}"}, 500