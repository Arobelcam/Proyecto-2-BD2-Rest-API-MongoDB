from flask import request, Response, jsonify
from bson import json_util
from bson import ObjectId
import re
from config.mongodb import mongo
from datetime import datetime, timedelta

#Funcion de servicio crear pedidos
def crear_pedidos_servicio():
    data = request.get_json()

    # Aceptar un solo pedido o una lista
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return {"error": "El cuerpo debe ser un objeto o una lista de pedidos"}, 400

    pedidos_a_insertar = []
    for item in data:
        IdUsuario      = item.get('IdUsuario')
        IdRestaurante  = item.get('IdRestaurante')
        items          = item.get('items')
        total          = item.get('total')
        fecha_pedido   = item.get('fecha_pedido')
        estado         = item.get('estado')

        # Validar campos obligatorios
        if not all([IdUsuario, IdRestaurante, items, total, fecha_pedido, estado]):
            continue

        # Convertir ObjectId
        try:
            uid = ObjectId(IdUsuario)
            rid = ObjectId(IdRestaurante)
        except Exception:
            continue

        # Validar y convertir fecha
        try:
            if isinstance(fecha_pedido, str):
                fecha = datetime.fromisoformat(fecha_pedido)
            else:
                fecha = fecha_pedido
        except Exception:
            continue

        # Procesar items
        items_proc = []
        for it in items:
            pid = it.get('IdPlato')
            cantidad = it.get('cantidad')
            precio = it.get('precio')
            if not pid or cantidad is None or precio is None:
                continue
            try:
                pid_obj = ObjectId(pid)
                cantidad = int(cantidad)
                precio = float(precio)
            except Exception:
                continue
            items_proc.append({
                "IdPlato": pid_obj,
                "cantidad": cantidad,
                "precio": precio
            })
        if not items_proc:
            continue

        pedidos_a_insertar.append({
            "IdUsuario": uid,
            "IdRestaurante": rid,
            "items": items_proc,
            "total": float(total),
            "fecha_pedido": fecha,
            "estado": estado
        })

    if not pedidos_a_insertar:
        return {"error": "No se encontró ningún pedido válido para insertar"}, 400

    result = mongo.db.pedidos.insert_many(pedidos_a_insertar)
    return {
        "mensaje": f"{len(result.inserted_ids)} pedido(s) insertado(s) correctamente",
        "ids": [str(_id) for _id in result.inserted_ids]
    }

#Funcion de actualizar pedidos
def actualizar_pedidos_servicio():
    data = request.get_json()
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return {"error": "El cuerpo debe ser un objeto o lista de pedidos"}, 400

    actualizados = 0
    ids_actualizados = []
    for item in data:
        id_pedido = item.get('id')
        if not id_pedido:
            continue
        try:
            pid = ObjectId(id_pedido)
        except Exception:
            continue

        update_fields = {}
        if 'IdUsuario' in item:
            try:
                update_fields['IdUsuario'] = ObjectId(item['IdUsuario'])
            except:
                pass
        if 'IdRestaurante' in item:
            try:
                update_fields['IdRestaurante'] = ObjectId(item['IdRestaurante'])
            except:
                pass
        if 'items' in item:
            processed = []
            for it in item['items']:
                try:
                    processed.append({
                        "IdPlato": ObjectId(it['IdPlato']),
                        "cantidad": int(it['cantidad']),
                        "precio": float(it['precio'])
                    })
                except:
                    continue
            if processed:
                update_fields['items'] = processed
        if 'total' in item:
            try:
                update_fields['total'] = float(item['total'])
            except:
                pass
        if 'fecha_pedido' in item:
            try:
                fp = item['fecha_pedido']
                if isinstance(fp, str):
                    fp = datetime.fromisoformat(fp)
                update_fields['fecha_pedido'] = fp
            except:
                pass
        if 'estado' in item:
            update_fields['estado'] = item['estado']

        if not update_fields:
            continue

        res = mongo.db.pedidos.update_one(
            {"_id": pid},
            {"$set": update_fields}
        )
        if res.modified_count > 0:
            actualizados += 1
            ids_actualizados.append(str(pid))

    if actualizados == 0:
        return {"mensaje": "No se actualizó ningún pedido"}, 400

    return {
        "mensaje": f"{actualizados} pedido(s) actualizado(s) correctamente",
        "ids_actualizados": ids_actualizados
    }

#Funcion de servicio eliminar pedidos
def eliminar_pedidos_servicio():
    data = request.get_json()
    if isinstance(data, dict):
        ids = [data.get('id')]
    elif isinstance(data, list):
        ids = [item.get('id') if isinstance(item, dict) else item for item in data]
    elif isinstance(data, str):
        ids = [data]
    else:
        return {"error": "Formato de entrada no válido"}, 400

    try:
        ids_obj = [ObjectId(i) for i in ids if i]
    except Exception:
        return {"error": "Al menos un ID no es válido"}, 400

    if not ids_obj:
        return {"error": "No se proporcionaron IDs válidos"}, 400

    res = mongo.db.pedidos.delete_many({"_id": {"$in": ids_obj}})
    return {
        "mensaje": f"{res.deleted_count} pedido(s) eliminado(s) correctamente",
        "ids_eliminados": [str(i) for i in ids_obj]
    }
  
###CONSULTAS
#consultas a documentos
# Funcion de servicio para filtro  
def get_pedidos_filtros_servicio():
    data = request.get_json(silent=True) or request.args
    filtros = {}
    # Filtrar por IdUsuario
    if 'IdUsuario' in data:
        try:
            filtros['IdUsuario'] = ObjectId(data['IdUsuario'])
        except:
            return {"error": "'IdUsuario' inválido."}, 400

    # Filtrar por IdRestaurante
    if 'IdRestaurante' in data:
        try:
            filtros['IdRestaurante'] = ObjectId(data['IdRestaurante'])
        except:
            return {"error": "'IdRestaurante' inválido."}, 400

    # Filtrar por IdPlato dentro de items
    if 'IdPlato' in data:
        try:
            filtros['items.IdPlato'] = ObjectId(data['IdPlato'])
        except:
            return {"error": "'IdPlato' inválido."}, 400

    # Filtrar por estado (regex, case-insensitive)
    if 'estado' in data:
        filtros['estado'] = re.compile(f"^{re.escape(data['estado'])}$", re.IGNORECASE)

    # Filtrar por total
    if 'total' in data:
        try:
            filtros['total'] = float(data['total'])
        except:
            return {"error": "'total' debe ser un número."}, 400

    # Filtrar por fecha_pedido (ISO string)
    if 'fecha_pedido' in data:
        try:
            fecha = data['fecha_pedido']
            if isinstance(fecha, str):
                fecha = datetime.fromisoformat(fecha)
            filtros['fecha_pedido'] = fecha
        except:
            return {"error": "'fecha_pedido' debe ser fecha ISO válida."}, 400

    try:
        resultado = mongo.db.pedidos.find(filtros)
        return list(resultado)
    except Exception as e:
        return {"error": f"Error al filtrar pedidos: {str(e)}"}, 500

#Funcion de servicio para proyeccion de pedidos
def get_pedidos_proyeccion_servicio():
    """
    Permite mezclar inclusiones y exclusiones en la misma consulta.
    - Los campos con valor 1 se incluyen.
    - Los campos con valor 0 se excluyen.
    Si hay inclusiones, sólo aparecerán esos campos (más _id siempre).
    Luego se eliminan las exclusiones sobre ese subconjunto.
    Si no hay inclusiones, partimos de todo el documento y sólo quitamos las exclusiones.
    """
    data = request.get_json() or {}
    includes = [f for f, v in data.items() if v == 1]
    excludes = [f for f, v in data.items() if v == 0]

    # Traer documentos completos
    docs = list(mongo.db.pedidos.find())

    resultado = []
    for doc in docs:
        # Por defecto trabajamos con todo el doc
        if includes:
            # Sólo traer los incluidos + siempre _id
            new_doc = {'_id': doc['_id']}
            for f in includes:
                if f in doc:
                    new_doc[f] = doc[f]
        else:
            # Incluir todos
            new_doc = dict(doc)

        # Quitar los excluidos
        for f in excludes:
            new_doc.pop(f, None)

        resultado.append(new_doc)

    return resultado

#Funcion de servicio para ordenamiento de pedidos
def get_pedidos_ordenamiento_servicio():
    data = request.get_json() or {}
    campo = data.get('campo')
    orden = data.get('orden')

    if not campo or orden not in (1, -1):
        return {"error": "Debes enviar 'campo' y 'orden' (1 o -1)."}, 400

    campos_validos = ['fecha_pedido', 'total', 'estado']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido para ordenamiento."}, 400

    try:
        cursor = mongo.db.pedidos.find({}).sort(campo, orden)
        return list(cursor)
    except Exception as e:
        return {"error": f"Error al ordenar pedidos: {str(e)}"}, 500
  
  #Funcion de servicio limits pedidos  
def get_pedidos_limit_servicio():
    """
    Limita la cantidad de pedidos devueltos.
    Query string: ?limit=<n>
    """
    data = request.args
    try:
        limit = int(data.get('limit', 10))
        if limit < 0:
            raise ValueError()
    except ValueError:
        return {"error": "'limit' debe ser un entero ≥ 0."}, 400

    try:
        cursor = mongo.db.pedidos.find({}).limit(limit)
        return list(cursor)
    except Exception as e:
        return {"error": f"Error al aplicar limit: {str(e)}"}, 500

#Funcion de servicio skip pedidos
def get_pedidos_skip_servicio():
    """
    Omite la cantidad de pedidos especificada.
    Query string: ?skip=<n>
    """
    data = request.args
    try:
        skip = int(data.get('skip', 0))
        if skip < 0:
            raise ValueError()
    except ValueError:
        return {"error": "'skip' debe ser un entero ≥ 0."}, 400

    try:
        cursor = mongo.db.pedidos.find({}).skip(skip)
        return list(cursor)
    except Exception as e:
        return {"error": f"Error al aplicar skip: {str(e)}"}, 500

#Counsultas por agregacion
#Simples
#Funcion de servicio count pedidos
def get_pedidos_count_servicio():
    
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

    # IdPlato dentro de items
    if 'IdPlato' in data:
        try:
            filtros['items.IdPlato'] = ObjectId(data['IdPlato'])
        except:
            return {"error": "'IdPlato' inválido."}, 400

    # Estado (match exacto, case-insensitive)
    if 'estado' in data:
        filtros['estado'] = re.compile(f"^{re.escape(data['estado'])}$", re.IGNORECASE)

    # Total
    if 'total' in data:
        try:
            filtros['total'] = float(data['total'])
        except:
            return {"error": "'total' debe ser un número."}, 400

    # Fecha de pedido (ISO string)
    if 'fecha_pedido' in data:
        try:
            fecha = data['fecha_pedido']
            if isinstance(fecha, str):
                fecha = datetime.fromisoformat(fecha)
            filtros['fecha_pedido'] = fecha
        except:
            return {"error": "'fecha_pedido' debe ser ISO date válido."}, 400

    try:
        count = mongo.db.pedidos.count_documents(filtros)
        return {"count": count}
    except Exception as e:
        return {"error": f"Error al contar documentos: {str(e)}"}, 500
 
 #Funcion de servicio distinct para pedidos   
def get_pedidos_distinct_servicio():
    """
    Devuelve valores únicos de un campo de pedidos.
    Campos válidos: estado, IdUsuario, IdRestaurante, total, fecha_pedido
    """
    data = request.args
    campo = data.get('campo', '')

    # Ahora incluimos total y fecha_pedido
    campos_validos = ['estado', 'IdUsuario', 'IdRestaurante', 'total', 'fecha_pedido']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido para distinct."}, 400

    try:
        valores = mongo.db.pedidos.distinct(campo)

        # Serializar ObjectId y datetime a str
        if campo in ('IdUsuario', 'IdRestaurante'):
            valores = [str(v) for v in valores]
        elif campo == 'fecha_pedido':
            valores = [v.isoformat() if isinstance(v, datetime) else v for v in valores]

        return {campo: valores}
    except Exception as e:
        return {"error": f"Error en distinct: {str(e)}"}, 500

#Funcion de servicio para match pedidos
def get_pedidos_match_servicio():
    """
    Aplica un $match en pedidos. Ahora maneja fecha_pedido correctamente:
    - Si el usuario pasa 'YYYY-MM-DD', se filtran todos los pedidos de ese día.
    - Si pasa un ISO completo 'YYYY-MM-DDTHH:MM:SS', se filtra ese instante exacto.
    """
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

    # IdPlato dentro de items
    if 'IdPlato' in data:
        try:
            filtros['items.IdPlato'] = ObjectId(data['IdPlato'])
        except:
            return {"error": "'IdPlato' inválido."}, 400

    # Estado
    if 'estado' in data:
        filtros['estado'] = re.compile(f"^{re.escape(data['estado'])}$", re.IGNORECASE)

    # Fecha de pedido
    if 'fecha_pedido' in data:
        fecha_str = data['fecha_pedido']
        try:
            # Parse ISO. Si viene sólo 'YYYY-MM-DD', fromisoformat crea datetime a medianoche.
            fecha = datetime.fromisoformat(fecha_str)
        except Exception:
            return {"error": "'fecha_pedido' debe ser ISO date válido."}, 400

        # Si el string es sólo fecha (10 caracteres), hacemos rango de un día
        if len(fecha_str) == 10:
            inicio = fecha
            fin = inicio + timedelta(days=1)
            filtros['fecha_pedido'] = {"$gte": inicio, "$lt": fin}
        else:
            # Fecha+hora exacta
            filtros['fecha_pedido'] = fecha

    try:
        pipeline = [{'$match': filtros}]
        resultados = list(mongo.db.pedidos.aggregate(pipeline))
        return resultados
    except Exception as e:
        return {"error": f"Error en match: {str(e)}"}, 500

#Funcion de servicios group pedidos
def get_pedidos_group_servicio():
    data = request.args
    campo = data.get('campo', '')
    campos_validos = ['estado', 'IdUsuario', 'IdRestaurante']
    if campo not in campos_validos:
        return {"error": f"El campo '{campo}' no es válido para group."}, 400

    try:
        pipeline = [
            {'$group': {
                '_id': f'${campo}',
                'total_pedidos': {'$sum': 1},
                'total_monto':   {'$sum': '$total'}
            }}
        ]
        resultados = list(mongo.db.pedidos.aggregate(pipeline))
        # Convertir ObjectId a str si agrupamos por IdUsuario/IdRestaurante
        if campo in ('IdUsuario', 'IdRestaurante'):
            for doc in resultados:
                doc['_id'] = str(doc['_id'])
        return resultados
    except Exception as e:
        return {"error": f"Error en group: {str(e)}"}, 500

#Funcion de servicio de push pedidos
def push_pedido_servicio():
    data = request.get_json()
    pedido_id = data.get('pedido_id')
    item = data.get('item')

    # Validar parámetros
    if not pedido_id or not item:
        return {"error": "Faltan 'pedido_id' o 'item'."}, 400
    try:
        pid = ObjectId(pedido_id)
    except:
        return {"error": "ID de pedido inválido."}, 400

    # Validar estructura de item
    try:
        ip = ObjectId(item['IdPlato'])
        cantidad = int(item['cantidad'])
        precio = float(item['precio'])
    except Exception:
        return {"error": "El 'item' debe tener IdPlato (ObjectId), cantidad (int) y precio (float)."}, 400

    nuevo_item = {"IdPlato": ip, "cantidad": cantidad, "precio": precio}

    # Push
    res = mongo.db.pedidos.update_one(
        {"_id": pid},
        {"$push": {"items": nuevo_item}}
    )
    if res.matched_count:
        return {"message": "Item agregado correctamente."}
    else:
        return {"error": "Pedido no encontrado."}, 404

#Funcion de servicio de pull pedidos
def pull_pedido_servicio():
    """
    Elimina de `items` todos los subdocumentos cuyo IdPlato coincida.
    Parámetros JSON:
      - pedido_id: str ObjectId del pedido
      - IdPlato:   str ObjectId del plato a quitar
    """
    data = request.get_json()
    pedido_id = data.get('pedido_id')
    id_plato = data.get('IdPlato')

    # Validar parámetros
    if not pedido_id or not id_plato:
        return {"error": "Faltan 'pedido_id' o 'IdPlato'."}, 400

    # Convertir strings a ObjectId
    try:
        pedido_obj_id = ObjectId(pedido_id)
    except Exception:
        return {"error": f"El 'pedido_id' no es un ObjectId válido: {pedido_id}"}, 400

    try:
        plato_obj_id = ObjectId(id_plato)
    except Exception:
        return {"error": f"El 'IdPlato' no es un ObjectId válido: {id_plato}"}, 400

    # Ejecutar $pull
    res = mongo.db.pedidos.update_one(
        {"_id": pedido_obj_id},
        {"$pull": {"items": {"IdPlato": plato_obj_id}}}
    )

    if res.modified_count > 0:
        return {"message": f"Item con IdPlato={id_plato} removido correctamente."}
    elif res.matched_count:
        # Se encontró el pedido pero no el item
        return {"message": f"No se encontró ningún item con IdPlato={id_plato} en este pedido."}
    else:
        return {"error": "Pedido no encontrado."}, 404

#Funcion de servicio addtoset pedidos
def add_to_set_pedido_servicio():
    data = request.get_json()
    pedido_id = data.get('pedido_id')
    item = data.get('item')

    if not pedido_id or not item:
        return {"error": "Faltan 'pedido_id' o 'item'."}, 400
    try:
        pid = ObjectId(pedido_id)
        ip = ObjectId(item['IdPlato'])
        cantidad = int(item['cantidad'])
        precio = float(item['precio'])
    except Exception:
        return {"error": "Parámetros de item inválidos."}, 400

    nuevo_item = {"IdPlato": ip, "cantidad": cantidad, "precio": precio}

    # Verificar existencia por IdPlato
    pedido = mongo.db.pedidos.find_one({"_id": pid, "items.IdPlato": ip}, {"items.$": 1})
    if pedido and pedido.get('items'):
        return {"message": "Ya existe un item con ese IdPlato, no se agregó."}

    res = mongo.db.pedidos.update_one(
        {"_id": pid},
        {"$addToSet": {"items": nuevo_item}}
    )
    if res.matched_count:
        return {"message": "Item agregado exitosamente (addToSet)."}
    else:
        return {"error": "Pedido no encontrado."}, 404
  
#Consulta agregacion para manejo de embeddeds
#Funcion de servicio para lookup  
def lookup_pedidos_servicio():
    data = request.get_json()
    pedido_id = data.get('pedido_id')
    if not pedido_id:
        return {"error": "Falta el parámetro 'pedido_id'."}, 400

    try:
        pedido_obj_id = ObjectId(pedido_id)
    except Exception as e:
        return {"error": f"ID de pedido inválido: {str(e)}"}, 400

    pipeline = [
        {"$match": {"_id": pedido_obj_id}},
        {"$unwind": "$items"},
        {"$lookup": {
            "from": "menu",
            "localField": "items.IdPlato",
            "foreignField": "_id",
            "as": "items.detalle"
        }},
        {"$unwind": {"path": "$items.detalle", "preserveNullAndEmptyArrays": True}},
        {"$group": {
            "_id": "$_id",
            "IdUsuario":      {"$first": "$IdUsuario"},
            "IdRestaurante":  {"$first": "$IdRestaurante"},
            "fecha_pedido":   {"$first": "$fecha_pedido"},
            "estado":         {"$first": "$estado"},
            "total":          {"$first": "$total"},
            "items":          {"$push": "$items"}
        }}
    ]

    resultado = list(mongo.db.pedidos.aggregate(pipeline))
    if not resultado:
        return {"error": "Pedido no encontrado."}, 404

    pedido = resultado[0]
    # convertir ObjectId a str en resultado
    pedido["IdUsuario"] = str(pedido["IdUsuario"])
    pedido["IdRestaurante"] = str(pedido["IdRestaurante"])
    pedido["_id"] = str(pedido["_id"])
    for it in pedido["items"]:
        it["IdPlato"] = str(it["IdPlato"])
        if isinstance(it.get("detalle", {}).get("_id"), ObjectId):
            it["detalle"]["_id"] = str(it["detalle"]["_id"])

    return {"pedido_con_detalle": pedido}

#Funcion de servicio para aggregation pipeline pedidos
def aggregation_pipeline_pedidos_servicio():
    data = request.get_json() or {}
    estado   = data.get('estado')
    sort_by  = data.get('sort_by', 'cantidad')
    limit    = data.get('limit', 5)

    # Validaciones
    if not estado:
        return {"error": "El campo 'estado' es requerido."}, 400
    if sort_by not in ('cantidad', 'ingresos'):
        return {"error": "'sort_by' debe ser 'cantidad' o 'ingresos'."}, 400
    try:
        limit = int(limit)
        if limit <= 0:
            raise ValueError()
    except:
        return {"error": "'limit' debe ser un entero mayor que 0."}, 400

    # Definir campo de ordenamiento
    sort_field = 'cantidad_total' if sort_by == 'cantidad' else 'ingresos_totales'

    pipeline = [
        # 1) Filtrar por estado
        { "$match": { "estado": estado } },

        # 2) Unwind de items
        { "$unwind": "$items" },

        # 3) Agrupar por IdPlato
        { "$group": {
            "_id": "$items.IdPlato",
            "cantidad_total": { "$sum": "$items.cantidad" },
            "ingresos_totales": { 
                "$sum": { 
                    "$multiply": ["$items.cantidad", "$items.precio"] 
                } 
            }
        }},

        # 4) Ordenar según el criterio
        { "$sort": { sort_field: -1 } },

        # 5) Limitar resultados
        { "$limit": limit }
    ]

    try:
        raw = list(mongo.db.pedidos.aggregate(pipeline))
    except Exception as e:
        return {"error": f"Error al ejecutar pipeline: {str(e)}"}, 500

    # Serializar ObjectId a string
    resultado = []
    for doc in raw:
        resultado.append({
            "IdPlato": str(doc["_id"]),
            "cantidad_total": doc["cantidad_total"],
            "ingresos_totales": doc["ingresos_totales"]
        })

    if not resultado:
        return {"error": "No se encontraron resultados para esos criterios."}, 404

    return {"resultado": resultado}