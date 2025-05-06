from flask import request, Response, jsonify
from bson import json_util
from bson import ObjectId
import re
from config.mongodb import mongo
from datetime import datetime, timedelta

#Funcion de servicio para crear reseña
def crear_reseñas_servicio():
    data = request.get_json()

    # Aceptar un solo objeto o lista
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return {"error": "El cuerpo debe ser un objeto o una lista de reseñas"}, 400

    docs = []
    for item in data:
        uid = item.get('IdUsuario')
        rid = item.get('IdRestaurante')
        pid = item.get('IdPedido')
        calif = item.get('calificacion')
        comentario = item.get('comentario')
        fecha = item.get('fecha')

        # Validar campos obligatorios
        if not all([uid, rid, pid, calif is not None, comentario, fecha]):
            continue

        try:
            uid_obj = ObjectId(uid)
            rid_obj = ObjectId(rid)
            pid_obj = ObjectId(pid)
        except Exception:
            continue

        # Parsear fecha ISO o asumir objeto datetime
        try:
            if isinstance(fecha, str):
                fecha_dt = datetime.fromisoformat(fecha)
            else:
                fecha_dt = fecha
        except Exception:
            continue

        try:
            calif_int = int(calif)
        except Exception:
            continue

        docs.append({
            "IdUsuario": uid_obj,
            "IdRestaurante": rid_obj,
            "IdPedido": pid_obj,
            "calificacion": calif_int,
            "comentario": comentario,
            "fecha": fecha_dt
        })

    if not docs:
        return {"error": "No se encontró ninguna reseña válida para insertar"}, 400

    result = mongo.db.reseñas.insert_many(docs)
    return {
        "mensaje": f"{len(result.inserted_ids)} reseña(s) insertada(s) correctamente",
        "ids": [str(_id) for _id in result.inserted_ids]
    }

#Funcion de servicio para actualizar reseñas
def actualizar_reseñas_servicio():
    data = request.get_json()

    # Aceptar objeto o lista
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return {"error": "El cuerpo debe ser un objeto o lista de reseñas"}, 400

    updated = 0
    ids_upd = []
    for item in data:
        rid = item.get('id')
        if not rid:
            continue
        try:
            obj_id = ObjectId(rid)
        except Exception:
            continue

        fields = {}
        if 'IdUsuario' in item:
            try: fields['IdUsuario'] = ObjectId(item['IdUsuario'])
            except: pass
        if 'IdRestaurante' in item:
            try: fields['IdRestaurante'] = ObjectId(item['IdRestaurante'])
            except: pass
        if 'IdPedido' in item:
            try: fields['IdPedido'] = ObjectId(item['IdPedido'])
            except: pass
        if 'calificacion' in item:
            try: fields['calificacion'] = int(item['calificacion'])
            except: pass
        if 'comentario' in item:
            fields['comentario'] = item['comentario']
        if 'fecha' in item:
            try:
                f = item['fecha']
                if isinstance(f, str):
                    f = datetime.fromisoformat(f)
                fields['fecha'] = f
            except: pass

        if not fields:
            continue

        res = mongo.db.reseñas.update_one({"_id": obj_id}, {"$set": fields})
        if res.modified_count > 0:
            updated += 1
            ids_upd.append(str(obj_id))

    if updated == 0:
        return {"mensaje": "No se actualizó ninguna reseña"}, 400

    return {
        "mensaje": f"{updated} reseña(s) actualizada(s) correctamente",
        "ids_actualizados": ids_upd
    }

#Funcion de servicio para eliminar reseñas
def eliminar_reseñas_servicio():
    data = request.get_json()

    # Aceptar dict, list o string
    if isinstance(data, dict):
        ids = [data.get('id')]
    elif isinstance(data, list):
        ids = [item.get('id') if isinstance(item, dict) else item for item in data]
    elif isinstance(data, str):
        ids = [data]
    else:
        return {"error": "Formato de entrada no válido"}, 400

    # Convertir a ObjectId y filtrar vacíos
    obj_ids = []
    for i in ids:
        try:
            if i:
                obj_ids.append(ObjectId(i))
        except:
            continue

    if not obj_ids:
        return {"error": "No se proporcionaron IDs válidos"}, 400

    res = mongo.db.reseñas.delete_many({"_id": {"$in": obj_ids}})
    return {
        "mensaje": f"{res.deleted_count} reseña(s) eliminada(s) correctamente",
        "ids_eliminados": [str(i) for i in obj_ids]
    }
    
#Consultas
#consultas a documentos 
#Funcion de servicio filtro reseñas
def get_reseñas_filtros_servicio():
    data = request.get_json(silent=True) or request.args
    filtros = {}

    # IdUsuario
    if 'IdUsuario' in data:
        try:
            filtros['IdUsuario'] = ObjectId(data['IdUsuario'])
        except:
            return {"error": "'IdUsuario' inválido."}, 400

    # IdRestaurante
    if 'IdRestaurante' in data:
        try:
            filtros['IdRestaurante'] = ObjectId(data['IdRestaurante'])
        except:
            return {"error": "'IdRestaurante' inválido."}, 400

    # IdPedido
    if 'IdPedido' in data:
        try:
            filtros['IdPedido'] = ObjectId(data['IdPedido'])
        except:
            return {"error": "'IdPedido' inválido."}, 400

    # Calificación
    if 'calificacion' in data:
        try:
            filtros['calificacion'] = int(data['calificacion'])
        except:
            return {"error": "'calificacion' debe ser entero."}, 400

    # Comentario
    if 'comentario' in data:
        filtros['comentario'] = re.compile(f".*{re.escape(data['comentario'])}.*", re.IGNORECASE)

    # Fecha
    if 'fecha' in data:
        fecha_str = data['fecha']
        try:
            fecha = datetime.fromisoformat(fecha_str)
        except:
            return {"error": "'fecha' debe ser ISO date válido."}, 400
        if len(fecha_str) == 10:
            inicio = fecha
            fin = inicio.replace(hour=23, minute=59, second=59, microsecond=999999)
            filtros['fecha'] = {"$gte": inicio, "$lte": fin}
        else:
            filtros['fecha'] = fecha

    try:
        resultados = list(mongo.db.reseñas.find(filtros))
        return resultados
    except Exception as e:
        return {"error": f"Error al filtrar reseñas: {str(e)}"}, 500

#Funcion de servicio proyeccion reseña
def get_reseñas_proyeccion_servicio():
    data = request.get_json() or {}
    includes = [f for f, v in data.items() if v == 1]
    excludes = [f for f, v in data.items() if v == 0]

    # Traer todos los documentos
    try:
        docs = list(mongo.db.reseñas.find())
    except Exception as e:
        return {"error": f"Error al obtener reseñas: {str(e)}"}, 500

    resultado = []
    for doc in docs:
        if includes:
            new_doc = {'_id': doc['_id']}
            for f in includes:
                if f in doc:
                    new_doc[f] = doc[f]
        else:
            new_doc = dict(doc)
        for f in excludes:
            new_doc.pop(f, None)
        resultado.append(new_doc)

    return resultado

#Funcion de servicio ordenamienro reseñas
def get_reseñas_ordenamiento_servicio():
    """
    Ordena reseñas por:
      - calificacion (int)
      - fecha (date)
      - comentario (string)
    Request JSON: { "campo": <campo>, "orden": 1|-1 }
    """
    data = request.get_json() or {}
    campo = data.get('campo')
    orden = data.get('orden')

    if not campo or orden not in (1, -1):
        return {"error": "Debes enviar 'campo' (calificacion, fecha o comentario) y 'orden' (1 o -1)."}, 400

    campos_validos = ['calificacion', 'fecha', 'comentario']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido para ordenamiento."}, 400

    try:
        cursor = mongo.db.reseñas.find({}).sort(campo, orden)
        return list(cursor)
    except Exception as e:
        return {"error": f"Error al ordenar reseñas: {str(e)}"}, 500
    
#Funcion de servicio para limit
def get_reseñas_limit_servicio():
    data = request.args
    try:
        limit = int(data.get('limit', 10))
        if limit < 0:
            raise ValueError()
    except ValueError:
        return {"error": "'limit' debe ser un entero ≥ 0."}, 400

    try:
        cursor = mongo.db.reseñas.find({}).limit(limit)
        return list(cursor)
    except Exception as e:
        return {"error": f"Error al aplicar limit: {str(e)}"}, 500

#Funcion de servicio para skip
def get_reseñas_skip_servicio():
    data = request.args
    try:
        skip = int(data.get('skip', 0))
        if skip < 0:
            raise ValueError()
    except ValueError:
        return {"error": "'skip' debe ser un entero ≥ 0."}, 400

    try:
        cursor = mongo.db.reseñas.find({}).skip(skip)
        return list(cursor)
    except Exception as e:
        return {"error": f"Error al aplicar skip: {str(e)}"}, 500

#Consultas por agregacion
#Simples
def get_reseñas_count_servicio():
    data = request.args
    filtros = {}

    # IdUsuario
    if 'IdUsuario' in data:
        try:
            filtros['IdUsuario'] = ObjectId(data['IdUsuario'])
        except:
            return {"error": "'IdUsuario' inválido."}, 400

    # IdRestaurante
    if 'IdRestaurante' in data:
        try:
            filtros['IdRestaurante'] = ObjectId(data['IdRestaurante'])
        except:
            return {"error": "'IdRestaurante' inválido."}, 400

    # IdPedido
    if 'IdPedido' in data:
        try:
            filtros['IdPedido'] = ObjectId(data['IdPedido'])
        except:
            return {"error": "'IdPedido' inválido."}, 400

    # Calificación
    if 'calificacion' in data:
        try:
            filtros['calificacion'] = int(data['calificacion'])
        except:
            return {"error": "'calificacion' debe ser un entero."}, 400

    # Fecha
    if 'fecha' in data:
        fecha_str = data['fecha']
        try:
            fecha = datetime.fromisoformat(fecha_str)
        except:
            return {"error": "'fecha' debe ser ISO date válido."}, 400

        # si viene solo YYYY-MM-DD, rango de día completo
        if len(fecha_str) == 10:
            inicio = fecha
            fin = inicio + timedelta(days=1)
            filtros['fecha'] = {"$gte": inicio, "$lt": fin}
        else:
            filtros['fecha'] = fecha

    try:
        count = mongo.db.reseñas.count_documents(filtros)
        return {"count": count}
    except Exception as e:
        return {"error": f"Error al contar reseñas: {str(e)}"}, 500
  
#Funcion de servicio para distinct  
def get_reseñas_distinct_servicio():
    data = request.args
    campo = data.get('campo', '')
    campos_validos = ['IdUsuario', 'IdRestaurante', 'IdPedido', 'calificacion', 'comentario', 'fecha']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido para distinct."}, 400

    try:
        valores = mongo.db.reseñas.distinct(campo)
        # Serializar tipos especiales
        if campo in ('IdUsuario', 'IdRestaurante', 'IdPedido'):
            valores = [str(v) for v in valores]
        elif campo == 'fecha':
            valores = [v.isoformat() for v in valores if isinstance(v, datetime)]
        return {campo: valores}
    except Exception as e:
        return {"error": f"Error en distinct: {str(e)}"}, 500

#Funcion de servicio para match reseñas
def get_reseñas_match_servicio():
    data = request.args
    filtros = {}

    if 'IdUsuario' in data:
        try:
            filtros['IdUsuario'] = ObjectId(data['IdUsuario'])
        except:
            return {"error": "'IdUsuario' inválido."}, 400

    if 'IdRestaurante' in data:
        try:
            filtros['IdRestaurante'] = ObjectId(data['IdRestaurante'])
        except:
            return {"error": "'IdRestaurante' inválido."}, 400

    if 'IdPedido' in data:
        try:
            filtros['IdPedido'] = ObjectId(data['IdPedido'])
        except:
            return {"error": "'IdPedido' inválido."}, 400

    if 'calificacion' in data:
        try:
            filtros['calificacion'] = int(data['calificacion'])
        except:
            return {"error": "'calificacion' debe ser entero."}, 400

    if 'comentario' in data:
        filtros['comentario'] = re.compile(f".*{re.escape(data['comentario'])}.*", re.IGNORECASE)

    if 'fecha' in data:
        fecha_str = data['fecha']
        try:
            fecha = datetime.fromisoformat(fecha_str)
        except:
            return {"error": "'fecha' debe ser ISO date válido."}, 400
        if len(fecha_str) == 10:
            inicio = fecha
            fin = fecha + timedelta(days=1)
            filtros['fecha'] = {"$gte": inicio, "$lt": fin}
        else:
            filtros['fecha'] = fecha

    try:
        pipeline = [{'$match': filtros}]
        return list(mongo.db.reseñas.aggregate(pipeline))
    except Exception as e:
        return {"error": f"Error en match: {str(e)}"}, 500

#Funcion de servicio para group reseñas
def get_reseñas_group_servicio():
    data = request.args
    campo = data.get('campo', '')
    campos_validos = ['IdUsuario', 'IdRestaurante', 'IdPedido', 'calificacion', 'comentario', 'fecha']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido para group."}, 400

    # Cuando agrupamos por fecha, lo hacemos por día
    if campo == 'fecha':
        project_stage = {
            "$project": {
                "dia": { "$dateToString": { "format": "%Y-%m-%d", "date": "$fecha" } }
            }
        }
        group_id = "$dia"
    else:
        project_stage = None
        group_id = f"${campo}"

    pipeline = []
    if project_stage:
        pipeline.append(project_stage)
        pipeline.append({"$group": {"_id": "$dia", "total_reseñas": {"$sum": 1}}})
    else:
        pipeline.append({"$group": {"_id": group_id, "total_reseñas": {"$sum": 1}}})

    try:
        resultados = list(mongo.db.reseñas.aggregate(pipeline))
        # Serializar ObjectId para ids
        if campo in ('IdUsuario', 'IdRestaurante', 'IdPedido'):
            for doc in resultados:
                doc['_id'] = str(doc['_id'])
        return resultados
    except Exception as e:
        return {"error": f"Error en group: {str(e)}"}, 500
 
 