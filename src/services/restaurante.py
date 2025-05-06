from flask import request, Response, jsonify
from bson import json_util
from bson import ObjectId
import re
from config.mongodb import mongo

# Funcion de servici crear restaurantes
def crear_restaurantes_servicio():
    data = request.get_json()

    # Si recibes un solo restaurante (diccionario), lo conviertes en lista
    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        return {"error": "El cuerpo debe ser un objeto o una lista de restaurantes"}, 400

    restaurantes_a_insertar = []

    for item in data:
        nombre = item.get('nombre')
        descripcion = item.get('descripcion', '')
        calificacion = item.get('calificacion', 0.0)
        tipo_cocina = item.get('tipo_cocina', [])
        direccion = item.get('direccion', {})
        calle = direccion.get('calle')
        ciudad = direccion.get('ciudad')
        ubicacion = item.get('ubicacion', {})
        categoria = item.get('categoria', '')

        # Validar que los campos requeridos existan
        if not nombre or not calle or not ciudad or not tipo_cocina or not ubicacion:
            continue  # Salta restaurantes incompletos

        # Construir el restaurante
        restaurante = {
            "nombre": nombre,
            "descripcion": descripcion,
            "calificacion": calificacion,
            "tipo_cocina": tipo_cocina,
            "direccion": {
                "calle": calle,
                "ciudad": ciudad
            },
            "ubicacion": ubicacion,
            "categoria": categoria
        }

        restaurantes_a_insertar.append(restaurante)

    if not restaurantes_a_insertar:
        return {"error": "No se encontró ningún restaurante válido para insertar"}, 400

    # Insertar los restaurantes en la base de datos
    result = mongo.db.restaurantes.insert_many(restaurantes_a_insertar)

    return {
        "mensaje": f"{len(result.inserted_ids)} restaurante(s) insertado(s) correctamente",
        "ids": [str(_id) for _id in result.inserted_ids]
    }

#Funcion de servicio de actualizar restaurantes
def actualizar_restaurantes_servicio():
    data = request.get_json()

    if isinstance(data, dict):
        data = [data]  # Convertir a lista si es un solo objeto

    if not isinstance(data, list):
        return {"error": "El cuerpo debe ser un objeto o lista de restaurantes"}, 400

    actualizados = 0
    ids_actualizados = []

    for item in data:
        id_restaurante = item.get('id')
        if not id_restaurante:
            continue

        try:
            object_id = ObjectId(id_restaurante)
        except:
            continue  

        update_fields = {}

        # Campos que se pueden actualizar
        for campo in ['nombre', 'descripcion', 'calificacion', 'tipo_cocina', 'categoria']:
            if campo in item:
                update_fields[campo] = item[campo]

        if 'direccion' in item:
            direccion = item['direccion']
            if isinstance(direccion, dict):
                update_fields['direccion'] = {
                    'calle': direccion.get('calle'),
                    'ciudad': direccion.get('ciudad')
                }

        if 'ubicacion' in item:
            update_fields['ubicacion'] = item.get('ubicacion')

        if not update_fields:
            continue  # No hay nada que actualizar

        result = mongo.db.restaurantes.update_one(
            {"_id": object_id},
            {"$set": update_fields}
        )

        if result.modified_count > 0:
            actualizados += 1
            ids_actualizados.append(str(object_id))

    if actualizados == 0:
        return {"mensaje": "No se actualizó ningún restaurante"}, 400

    return {
        "mensaje": f"{actualizados} restaurante(s) actualizado(s) correctamente",
        "ids_actualizados": ids_actualizados
    }

#Funcion de servicio para eliminar restaurantes
def eliminar_restaurantes_servicio():
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

    resultado = mongo.db.restaurantes.delete_many({"_id": {"$in": ids_limpios}})

    return {
        "mensaje": f"{resultado.deleted_count} restaurante(s) eliminado(s) correctamente",
        "ids_eliminados": [str(id) for id in ids_limpios]
    }

#Funcion de validacion indices
def verificar_indice_y_consultar_restaurantes(filtros, orden=None):
    # Verificación para el índice compuesto del nombre y el tipo de cocina
    if 'nombre' in filtros and 'tipo_cocina' in filtros:
        if 'nombre_1_tipo_cocina_1' not in mongo.db.restaurantes.index_information():
            return {"error": "Consulta no optimizada. Usa índices en 'nombre' y 'tipo_cocina'."}, 400

    # Verificación para el índice de categoría
    if 'categoria' in filtros:
        if 'categoria_1' not in mongo.db.restaurantes.index_information():
            return {"error": "Consulta no optimizada. Usa el índice en 'categoria'."}, 400

    # Verificación para el índice de ubicación
    if 'ubicacion' in filtros:
        if 'ubicacion_2dsphere' not in mongo.db.restaurantes.index_information():
            return {"error": "Consulta no optimizada. Usa el índice 2dsphere en 'ubicacion'."}, 400

    # Realizar la consulta con los filtros y ordenamiento si aplica
    restaurantes = mongo.db.restaurantes.find(filtros).sort(orden) if orden else mongo.db.restaurantes.find(filtros)
    return list(restaurantes)

### CONSULTAS
#Consultas a documentos
#Funcion de servicio para filtro

def get_restaurantes_filtros_servicio():
    data = request.get_json()  
    if not data:  
        data = request.args  

    filtros = {}

    # Filtrar por 'nombre' con expresión regular
    if 'nombre' in data:
        filtros['nombre'] = re.compile(f"^{data['nombre']}$", re.IGNORECASE)
    
    # Filtrar por 'tipo_cocina' (como array, buscamos elementos específicos dentro del array)
    if 'tipo_cocina' in data:
        filtros['tipo_cocina'] = {"$in": data['tipo_cocina']}  # Buscamos si alguna de las cocinas en el array coincide
    
    # Filtrar por 'categoria'
    if 'categoria' in data:
        filtros['categoria'] = data['categoria']
    
    # Filtrar por 'calificacion'
    if 'calificacion' in data:
        filtros['calificacion'] = data['calificacion']

    # Filtrar por 'direccion'
    if 'direccion' in data:
        direccion_filtro = {}
        
        if 'calle' in data['direccion']:
            direccion_filtro['calle'] = re.compile(f".*{data['direccion']['calle']}.*", re.IGNORECASE)
        
        if 'ciudad' in data['direccion']:
            direccion_filtro['ciudad'] = re.compile(f".*{data['direccion']['ciudad']}.*", re.IGNORECASE)
        
        filtros['direccion'] = direccion_filtro

    # Filtrar por 'ubicacion' (usando la funcionalidad geoespacial de MongoDB, por ejemplo, cercanía a unas coordenadas específicas)
    if 'ubicacion' in data:
        if 'coordinates' in data['ubicacion']:
            # Asegúrate de que las coordenadas estén en el formato correcto [longitud, latitud]
            filtros['ubicacion'] = {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": data['ubicacion']['coordinates']  # Ejemplo: [long, lat]
                    },
                    "$maxDistance": 5000  # Opcional: limita la búsqueda a 5 km (ajusta según lo que necesites)
                }
            }

    # Ejecutar la consulta con los filtros
    restaurantes = mongo.db.restaurantes.find(filtros)
    
    # Devolvemos los resultados en formato lista
    return list(restaurantes)


# Funcion de servicio para proyeccion
def get_restaurantes_proyeccion_servicio():
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
    resultado = mongo.db.restaurantes.find({}, projection)
    return list(resultado)

# Funcion de servicio para ordenamiento
def get_restaurantes_ordenamiento_servicio():
    data = request.get_json()
    campo = data.get('campo')
    orden = data.get('orden')

    # Validaciones
    if not campo or orden not in (1, -1):
        return {"error": "Debes enviar 'campo' (nombre, tipo_cocina, calificacion) y 'orden' (1 o -1)."}, 400

    # Campos permitidos para ordenar
    campos_validos = ['nombre', 'calificacion', 'tipo_cocina']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido para ordenamiento."}, 400

    try:
        # Ejecutar la consulta con ordenamiento
        cursor = mongo.db.restaurantes.find({}).sort(campo, orden)
        return list(cursor)
    except Exception as e:
        return {"error": f"Ocurrió un error al ordenar: {str(e)}"}, 500

#Funcion de servicio para hacer limit a restaurantes
def get_restaurantes_limit_servicio():
    data = request.args
    limit = int(data.get('limit', 10))  # Definimos un límite por defecto

    filtros = {}

    # Verificar si hay filtros adicionales (por ejemplo, nombre, categoría, etc.)
    if 'nombre' in data:
        filtros['nombre'] = re.compile(f"^{data['nombre']}$", re.IGNORECASE)

    if 'categoria' in data:
        filtros['categoria'] = data['categoria']

    if 'calificacion' in data:
        filtros['calificacion'] = data['calificacion']

    if 'tipo_cocina' in data:
        filtros['tipo_cocina'] = {"$in": data['tipo_cocina']}  # Si hay varios valores, buscamos si el campo tipo_cocina contiene alguno

    if 'direccion' in data:
        direccion_filtro = {}
        if 'calle' in data['direccion']:
            direccion_filtro['calle'] = re.compile(f".*{data['direccion']['calle']}.*", re.IGNORECASE)

        if 'ciudad' in data['direccion']:
            direccion_filtro['ciudad'] = re.compile(f".*{data['direccion']['ciudad']}.*", re.IGNORECASE)

        filtros['direccion'] = direccion_filtro

    # Validar los índices
    resultado = verificar_indice_y_consultar(filtros)

    if isinstance(resultado, tuple): 
        return resultado

    # Aplicar limit sobre el cursor
    restaurantes = resultado.limit(limit)

    return list(restaurantes)

#Funcion de servicio para hacer skip a restaurantes
def get_restaurantes_skip_servicio():
    data = request.args
    skip = int(data.get('skip', 0))  # Por defecto, no saltar registros

    filtros = {}  # Si no hay filtros, se pasa un diccionario vacío

    # Verificar si hay filtros adicionales
    if 'nombre' in data:
        filtros['nombre'] = re.compile(f"^{data['nombre']}$", re.IGNORECASE)

    if 'categoria' in data:
        filtros['categoria'] = data['categoria']

    if 'calificacion' in data:
        filtros['calificacion'] = data['calificacion']

    if 'tipo_cocina' in data:
        filtros['tipo_cocina'] = {"$in": data['tipo_cocina']}  # Buscamos los valores dentro del array

    if 'direccion' in data:
        direccion_filtro = {}
        if 'calle' in data['direccion']:
            direccion_filtro['calle'] = re.compile(f".*{data['direccion']['calle']}.*", re.IGNORECASE)

        if 'ciudad' in data['direccion']:
            direccion_filtro['ciudad'] = re.compile(f".*{data['direccion']['ciudad']}.*", re.IGNORECASE)

        filtros['direccion'] = direccion_filtro

    # Validar los índices
    resultado = verificar_indice_y_consultar(filtros)

    if isinstance(resultado, tuple):  # Si se presenta un error con la consulta
        return resultado

    # Aplicar skip sobre el cursor
    restaurantes = resultado.skip(skip)

    return list(restaurantes)

#Funcion de servicio verificacion indices restaurantes
def verificar_indice_y_consultar(filtros):
    # Definimos los índices válidos para la colección de restaurantes
    indices_validos = ['nombre', 'categoria', 'calificacion', 'tipo_cocina', 'direccion']

    for campo in filtros.keys():
        if campo not in indices_validos:
            return {"error": f"El campo '{campo}' no es un campo indexado."}, 400

    # Si la consulta es válida, realizamos la consulta en la base de datos y devolvemos el cursor
    resultado = mongo.db.restaurantes.find(filtros)

    return resultado

#Consultas por agregacion
#Simple
def get_restaurantes_count_servicio():
    data = request.args
    filtros = {}

    # Si el parámetro 'calificacion' está presente, lo convertimos a un número
    if 'calificacion' in data:
        try:
            filtros['calificacion'] = float(data['calificacion'])  # Convertimos a float para asegurarnos que sea un número
        except ValueError:
            return {"error": "La calificación debe ser un número válido."}, 400

    # Si el parámetro 'tipo_cocina' está presente, lo agregamos al filtro
    if 'tipo_cocina' in data:
        tipo_cocina = data['tipo_cocina']
        # Si es un único valor, lo convertimos a una lista (aseguramos que sea un array)
        if not isinstance(tipo_cocina, list):
            tipo_cocina = [tipo_cocina]
        filtros['tipo_cocina'] = {"$in": tipo_cocina}  # Aseguramos que el filtro $in reciba un array

    # Si el parámetro 'nombre' está presente, lo agregamos al filtro
    if 'nombre' in data:
        filtros['nombre'] = data['nombre']

    # Si el parámetro 'categoria' está presente, lo agregamos al filtro
    if 'categoria' in data:
        filtros['categoria'] = data['categoria']

    # Si el parámetro 'direccion' está presente, lo agregamos al filtro
    if 'direccion' in data:
        direccion_filtro = {}
        if 'calle' in data['direccion']:
            direccion_filtro['calle'] = re.compile(f".*{data['direccion']['calle']}.*", re.IGNORECASE)

        if 'ciudad' in data['direccion']:
            direccion_filtro['ciudad'] = re.compile(f".*{data['direccion']['ciudad']}.*", re.IGNORECASE)

        filtros['direccion'] = direccion_filtro

    # Realizamos la consulta para obtener el número de documentos que cumplen con el filtro
    count = mongo.db.restaurantes.count_documents(filtros)

    return {"count": count}


# Funcion de servicio distinct
def get_restaurantes_distinct_servicio():
    data = request.args
    campo = data.get('campo', '')  # El campo en el que se va a buscar los valores distintos

    if not campo:
        return {"error": "El parámetro 'campo' es obligatorio para realizar la consulta distinct."}, 400

    # Verificar que el campo sea válido
    campos_validos = ['nombre', 'categoria', 'calificacion', 'tipo_cocina']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido para la operación distinct."}, 400

    # Realizar la consulta de distinct en el campo especificado
    resultado = mongo.db.restaurantes.distinct(campo)

    # Devolver los valores únicos encontrados
    return {campo: resultado}

#Funcion de servicio para match
def get_restaurantes_match_servicio():
    # Obtener los parámetros de la URL
    data = request.args
    filtros = {}

    # Si el parámetro 'nombre' está presente, lo agregamos al filtro
    if 'nombre' in data:
        filtros['nombre'] = data['nombre']

    # Si el parámetro 'categoria' está presente, lo agregamos al filtro
    if 'categoria' in data:
        filtros['categoria'] = data['categoria']

    # Si el parámetro 'calificacion' está presente, lo agregamos al filtro
    if 'calificacion' in data:
        try:
            filtros['calificacion'] = float(data['calificacion'])  # Convertir a número
        except ValueError:
            return {"error": "La calificación debe ser un número válido."}, 400

    # Si el parámetro 'tipo_cocina' está presente, lo agregamos al filtro
    if 'tipo_cocina' in data:
        tipo_cocina = data['tipo_cocina']
        # Si es un único valor, lo convertimos a una lista (aseguramos que sea un array)
        if not isinstance(tipo_cocina, list):
            tipo_cocina = [tipo_cocina]
        filtros['tipo_cocina'] = {"$in": tipo_cocina}  # Aseguramos que el filtro $in reciba un array

    # Crear el pipeline de agregación con el operador $match
    pipeline = [
        {"$match": filtros}  # Aplicamos el filtro usando $match
    ]
    
    # Ejecutamos el pipeline en la colección de restaurantes
    resultado = mongo.db.restaurantes.aggregate(pipeline)

    # Convertir el cursor en una lista y devolver los resultados
    return list(resultado)

#Funcion de servicio para group
def get_restaurantes_group_servicio():
    # Obtener los parámetros de la URL
    data = request.args
    filtros = {}

    # Si el parámetro 'categoria' está presente, lo agregamos al filtro
    if 'categoria' in data:
        filtros['categoria'] = data['categoria']

    # Crear el pipeline de agregación con el operador $group
    pipeline = [
        {"$match": filtros},  # Primero aplicamos el filtro con $match
        {"$group": {  # Luego agrupamos los resultados
            "_id": "$categoria",  # Agrupamos por el campo 'categoria'
            "total_restaurantes": {"$sum": 1}  # Contamos el total de restaurantes por categoría
        }}
    ]

    # Ejecutamos el pipeline en la colección de restaurantes
    resultado = mongo.db.restaurantes.aggregate(pipeline)

    # Convertir el cursor en una lista y devolver los resultados
    return list(resultado)

### Consultas agregacion manejo de arrays
#Funcion de servicio push
def push_restaurante_servicio():
    # Obtener los parámetros de la solicitud
    data = request.get_json()  # Obtener datos del cuerpo de la solicitud
    restaurante_id = data.get('restaurante_id')  # El ID del restaurante al que se agregará el valor
    campo = data.get('campo')  # El campo del array al que se agregará el valor
    valor = data.get('valor')  # El valor que se agregará al array

    if not restaurante_id or not campo or not valor:
        return {"error": "Faltan parámetros 'restaurante_id', 'campo' o 'valor'"}, 400

    # Convertir el restaurante_id a ObjectId de MongoDB si es necesario
    try:
        restaurante_id = ObjectId(restaurante_id)
    except Exception as e:
        return {"error": f"El ID de restaurante no es válido: {str(e)}"}, 400

    # Validar que el campo sea uno de los esperados
    campos_validos = ['tipo_cocina']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido."}, 400

    # Verificar si el campo es un array
    if campo != 'tipo_cocina':
        restaurante = mongo.db.restaurantes.find_one({"_id": restaurante_id})
        if not isinstance(restaurante.get(campo), list):
            return {"error": f"El campo '{campo}' no es un arreglo. No se puede usar el operador $push."}, 400

    # Realizar la operación $push para agregar el valor al array del campo correspondiente
    resultado = mongo.db.restaurantes.update_one(
        {"_id": restaurante_id},  # Filtro para el restaurante por ID
        {"$push": {campo: valor}}  # Agregar el valor al array del campo
    )

    # Verificar si se modificó el documento
    if resultado.matched_count > 0:
        return {"message": f"{valor} agregado exitosamente a {campo}."}
    else:
        return {"error": "Restaurante no encontrado."}, 404

#Funcion de servicio pull
def pull_restaurante_servicio():
    # Obtener los parámetros de la solicitud
    data = request.get_json()  # Obtener datos del cuerpo de la solicitud
    restaurante_id = data.get('restaurante_id')  # El ID del restaurante
    campo = data.get('campo')  # El campo del array del que se eliminará el valor
    valor = data.get('valor')  # El valor que se eliminará del array

    if not restaurante_id or not campo or not valor:
        return {"error": "Faltan parámetros 'restaurante_id', 'campo' o 'valor'"}, 400

    # Convertir el restaurante_id a ObjectId de MongoDB si es necesario
    try:
        restaurante_id = ObjectId(restaurante_id)
    except Exception as e:
        return {"error": f"El ID de restaurante no es válido: {str(e)}"}, 400

    # Validar que el campo sea uno de los esperados
    campos_validos = ['tipo_cocina']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido."}, 400

    # Verificar si el campo es "tipo_cocina" o no es un arreglo
    if campo != 'tipo_cocina':
        restaurante = mongo.db.restaurantes.find_one({"_id": restaurante_id})
        if not isinstance(restaurante.get(campo), list):
            return {"error": f"El campo '{campo}' no es un arreglo. No se puede usar el operador $pull."}, 400

    # Realizar la operación $pull para eliminar el valor del array del campo correspondiente
    resultado = mongo.db.restaurantes.update_one(
        {"_id": restaurante_id},  # Filtro para el restaurante por ID
        {"$pull": {campo: valor}}  # Eliminar el valor del array del campo
    )

    # Verificar si se modificó el documento
    if resultado.matched_count > 0:
        return {"message": f"{valor} eliminado exitosamente de {campo}."}
    else:
        return {"error": "Restaurante no encontrado."}, 404

# Funcion de servicio AddToSET
def add_to_set_restaurante_servicio():
    # Obtener los parámetros de la solicitud
    data = request.get_json()  # Obtener datos del cuerpo de la solicitud
    restaurante_id = data.get('restaurante_id')  # El ID del restaurante
    campo = data.get('campo')  # El campo del array al que se agregará el valor
    valor = data.get('valor')  # El valor que se agregará al array

    if not restaurante_id or not campo or not valor:
        return {"error": "Faltan parámetros 'restaurante_id', 'campo' o 'valor'"}, 400

    # Convertir el restaurante_id a ObjectId de MongoDB si es necesario
    try:
        restaurante_id = ObjectId(restaurante_id)
    except Exception as e:
        return {"error": f"El ID de restaurante no es válido: {str(e)}"}, 400

    # Validar que el campo sea uno de los esperados
    campos_validos = ['tipo_cocina']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido."}, 400

    # Verificar si el campo es "tipo_cocina" o no es un arreglo
    if campo != 'tipo_cocina':
        restaurante = mongo.db.restaurantes.find_one({"_id": restaurante_id})
        if not isinstance(restaurante.get(campo), list):
            return {"error": f"El campo '{campo}' no es un arreglo. No se puede usar el operador $addToSet."}, 400

    # Verificar si el valor ya existe en el array para evitar duplicados
    restaurante = mongo.db.restaurantes.find_one({"_id": restaurante_id})
    if restaurante and valor in restaurante.get(campo, []):
        return {"message": f"El valor '{valor}' ya está presente en el campo '{campo}', no se agregó."}

    # Realizar la operación $addToSet para agregar el valor al array del campo correspondiente
    resultado = mongo.db.restaurantes.update_one(
        {"_id": restaurante_id},  # Filtro para el restaurante por ID
        {"$addToSet": {campo: valor}}  # Agregar el valor al array del campo
    )

    # Verificar si se modificó el documento
    if resultado.matched_count > 0:
        return {"message": f"{valor} agregado exitosamente a {campo}."}
    else:
        return {"error": "Restaurante no encontrado."}, 404

### Consulta por agregacion manejo embedded
#Funcion de servicio project
def project_restaurante_servicio():
    # Obtener los parámetros de la solicitud
    data = request.get_json()  # Obtener datos del cuerpo de la solicitud
    restaurante_id = data.get('restaurante_id')  # El ID del restaurante
    campos_proyectados = data.get('campos')  # Los campos a proyectar (como una lista de cadenas)

    if not restaurante_id or not campos_proyectados:
        return {"error": "Faltan parámetros 'restaurante_id' o 'campos'"}, 400

    # Convertir el restaurante_id a ObjectId de MongoDB si es necesario
    try:
        restaurante_id = ObjectId(restaurante_id)
    except Exception as e:
        return {"error": f"El ID de restaurante no es válido: {str(e)}"}, 400

    # Realizar la operación $project para seleccionar los campos deseados
    try:
        # Creamos un diccionario con los campos a proyectar
        campos_dict = {campo: 1 for campo in campos_proyectados}  # Todos los campos seleccionados se proyectan con valor 1

        # Realizar la consulta con $project
        restaurante = mongo.db.restaurantes.find_one({"_id": restaurante_id}, campos_dict)

        if restaurante:
            return {"restaurante": restaurante}
        else:
            return {"error": "Restaurante no encontrado."}, 404
    except Exception as e:
        return {"error": f"Error al realizar la proyección: {str(e)}"}, 500

#Funcion de servicio unwind
def unwind_restaurante_servicio():
    # Obtener los parámetros de la URL
    data = request.get_json()  # Obtener datos del cuerpo de la solicitud
    restaurante_id = data.get('restaurante_id')  # El ID del restaurante
    campo = data.get('campo')  # El campo de arreglo que se va a descomponer

    if not restaurante_id or not campo:
        return {"error": "Faltan parámetros 'restaurante_id' o 'campo'"}, 400

    # Convertir el restaurante_id a ObjectId de MongoDB si es necesario
    try:
        restaurante_id = ObjectId(restaurante_id)
    except Exception as e:
        return {"error": f"El ID de restaurante no es válido: {str(e)}"}, 400

    # Validar que el campo sea un arreglo
    campos_validos = ['tipo_cocina']  # Se espera que el campo sea "tipo_cocina"
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido para la operación de unwind."}, 400

    # Realizar la operación $unwind para descomponer el arreglo
    try:
        # Realizar la consulta con $unwind
        pipeline = [
            {"$match": {"_id": restaurante_id}},  # Filtramos el documento por ID
            {"$unwind": f"${campo}"}  # Aplicamos el unwind al campo específico
        ]
        
        resultado = list(mongo.db.restaurantes.aggregate(pipeline))  # Ejecutamos la agregación

        if resultado:
            return {"restaurante_descompuesto": resultado}
        else:
            return {"error": "Restaurante no encontrado."}, 404
    except Exception as e:
        return {"error": f"Error al realizar el unwind: {str(e)}"}, 500
    
    #Funcion de servicio lookup
def lookup_restaurante_servicio():
    # Obtener los parámetros de la solicitud
    data = request.get_json()  # Obtener datos del cuerpo de la solicitud
    restaurante_id = data.get('restaurante_id')  # El ID del restaurante para hacer el lookup
    coleccion_lookup = data.get('coleccion_lookup')  # El nombre de la colección con la que hacer el join
    campo_local = data.get('campo_local')  # El campo en la colección actual para hacer el join
    campo_foreign = data.get('campo_foreign')  # El campo en la colección de lookup para hacer el join

    # Validar que todos los parámetros estén presentes
    if not restaurante_id or not coleccion_lookup or not campo_local or not campo_foreign:
        return {"error": "Faltan parámetros 'restaurante_id', 'coleccion_lookup', 'campo_local' o 'campo_foreign'"}, 400

    # Convertir el restaurante_id a ObjectId de MongoDB
    try:
        restaurante_id = ObjectId(restaurante_id)  # Intentamos convertir a ObjectId
    except Exception as e:
        return {"error": f"El ID de restaurante no es válido: {str(e)}"}, 400

    # Realizar la operación de agregación con $lookup
    try:
        pipeline = [
            {
                "$lookup": {
                    "from": coleccion_lookup,  # Colección con la que se hace el join
                    "localField": campo_local,  # Campo de la colección actual
                    "foreignField": campo_foreign,  # Campo de la colección de lookup
                    "as": "informacion_combinada"  # Nombre del campo donde se guardarán los resultados
                }
            },
            {
                "$match": {"_id": restaurante_id}  # Filtrar por el restaurante_id convertido a ObjectId
            },
            {
                "$project": {
                    "nombre": 1,                # Mostrar el nombre del restaurante
                    "descripcion": 1,           # Mostrar la descripción del restaurante
                    "informacion_combinada": 1  # Mostrar los documentos combinados
                }
            }
        ]

        # Ejecutar la agregación
        resultado = list(mongo.db.restaurantes.aggregate(pipeline))  # Ejecutar la pipeline de agregación

        if resultado:
            return {"restaurante_con_info": resultado}
        else:
            return {"error": "Restaurante no encontrado."}, 404
    except Exception as e:
        return {"error": f"Error al realizar el lookup: {str(e)}"}, 500
   
   ### Agreggation pipeline restaurante
def aggregation_pipeline_r_servicio():
    # Obtener los parámetros de la solicitud
    data = request.get_json()
    tipo_cocina = data.get('tipo_cocina')    # Tipo de cocina para filtrar (por ejemplo: ["mexicana", "italiana"])
    sort_order = data.get('sort_order', -1)  # Orden (1 para ascendente, -1 para descendente)
    limit = data.get('limit', 5)  # Limite de resultados

    # Validaciones de entrada
    if not tipo_cocina:
        return {"error": "El campo 'tipo_cocina' es requerido."}, 400
    if not isinstance(tipo_cocina, list):
        return {"error": "'tipo_cocina' debe ser una lista."}, 400
    if not isinstance(sort_order, int) or sort_order not in [-1, 1]:
        return {"error": "'sort_order' debe ser 1 (ascendente) o -1 (descendente)."}, 400
    if not isinstance(limit, int) or limit <= 0:
        return {"error": "'limit' debe ser un número entero mayor a 0."}, 400

    try:
        # Construir la pipeline de agregación
        pipeline = [
            # Stage 1: Filtrar restaurantes por tipo de cocina
            { "$match": { "tipo_cocina": { "$in": tipo_cocina } } },

            # Stage 2: Agrupar por nombre de restaurante y contar los elementos
            { "$group": { "_id": "$nombre", "total_restaurantes": { "$sum": 1 }, "calificacion_promedio": { "$avg": "$calificacion" } } },

            # Stage 3: Proyectar el nombre, la cantidad de restaurantes y la calificación promedio
            { "$project": { "_id": 1, "total_restaurantes": 1, "calificacion_promedio": 1 } },

            # Stage 4: Ordenar por la calificación promedio en el orden especificado
            { "$sort": { "calificacion_promedio": sort_order } },

            # Stage 5: Limitar los resultados según el parámetro 'limit'
            { "$limit": limit }
        ]

        # Ejecutar la agregación en la colección 'restaurantes'
        resultado = list(mongo.db.restaurantes.aggregate(pipeline))

        if resultado:
            return {"resultado": resultado}
        else:
            return {"error": "No se encontraron resultados para los criterios especificados."}, 404

    except Exception as e:
        return {"error": f"Error al ejecutar la pipeline: {str(e)}"}, 500


