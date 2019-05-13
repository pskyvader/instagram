from core.app import app
from core.database import database
from core.functions import functions
from .base_model import base_model
from .log import log
from .table import table
import json


class pedido(base_model):
    idname = 'idpedido'
    table = 'pedido'
    delete_cache = False

    @classmethod
    def getAll(cls, where={}, condiciones={}, select=""):
        from .table import table as table_model
        condiciones = condiciones.copy()
        where = where.copy()
        limit = None
        idpadre = None
        return_total = None
        connection = database.instance()
        fields = table_model.getByname(cls.table)
        if 'estado' not in where and app.front and 'estado' in fields:
            where['estado'] = True

        if 'idpadre' in where:
            if 'idpadre' in fields:
                idpadre = where['idpadre']
                if 'limit' in condiciones:
                    limit = condiciones['limit']
                    limit2 = 0
                    del condiciones['limit']

                if 'limit2' in condiciones:
                    if limit == None:
                        limit = 0
                    limit2 = condiciones['limit2']
                    del condiciones['limit2']
            del where['idpadre']

        if 'order' not in condiciones and 'orden' in fields:
            condiciones['order'] = 'orden ASC'

        if 'palabra' in condiciones:
            condiciones['buscar'] = {}
            if 'titulo' in fields:
                condiciones['buscar']['titulo'] = condiciones['palabra']

            if 'keywords' in fields:
                condiciones['buscar']['keywords'] = condiciones['palabra']

            if 'descripcion' in fields:
                condiciones['buscar']['descripcion'] = condiciones['palabra']

            if 'metadescripcion' in fields:
                condiciones['buscar']['metadescripcion'] = condiciones['palabra']

            if 'cookie_pedido' in fields:
                condiciones['buscar']['cookie_pedido'] = condiciones['palabra']

            if len(condiciones['buscar']) == 0:
                del condiciones['buscar']

        if select == 'total':
            return_total = True
            if idpadre != None:
                select = ''
        row = connection.get(cls.table, cls.idname, where, condiciones, select)
        deleted = False
        row_copy = []
        for r in row:
            deleted = False
            if 'idpadre' in r:
                if r['idpadre'] != '':
                    r['idpadre'] = json.loads(r['idpadre'])
                else:
                    r['idpadre'] = []
                if idpadre != None and idpadre not in r['idpadre']:
                    deleted = True

            if return_total == None:
                if not deleted and 'foto' in r:
                    if r['foto'] != '':
                        r['foto'] = json.loads(r['foto'])
                    else:
                        r['foto'] = []
                if not deleted and 'archivo' in r:
                    if r['archivo'] != '':
                        r['archivo'] = json.loads(r['archivo'])
                    else:
                        r['archivo'] = []

            if not deleted:
                row_copy.append(r)

        row = row_copy

        if limit != None:
            if limit2 == 0:
                row = row[0:limit]
            else:
                row = row[limit:limit2+1]

        if return_total != None:
            if idpadre != None:
                return len(row)
            else:
                return row[0]['total']
        else:
            return row

    @classmethod
    def insert(cls, set_query: dict,  loggging=True):
        fields     = table.getByname(cls.table)
        if not 'fecha_creacion' in set_query: set_query['fecha_creacion'] = functions.current_time()

        insert = database.create_data(fields, set_query)
        connection = database.instance()
        row = connection.insert(cls.table, cls.idname, insert)
        if isinstance(row, int) and row > 0:
            last_id = row
            if loggging:
                log.insert_log(cls.table, cls.idname, cls, insert)
                pass
            return last_id
        else:
            return row

    @classmethod
    def update(cls, set_query: dict, loggging=True):
        where = {cls.idname: set_query['id']}
        del set_query['id']
        connection = database.instance()
        row = connection.update(cls.table, cls.idname, set_query, where, cls.delete_cache)
        if loggging:
            log_register=set_query
            log_register.update(where)
            log.insert_log(cls.table, cls.idname, cls, log_register)
        if isinstance(row, bool) and row:
            row = where[cls.idname]
        return row

    @classmethod
    def delete(cls, id: int):
        where = {cls.idname: id}
        connection = database.instance()
        row = connection.delete(cls.table, cls.idname, where, cls.delete_cache)
        log.insert_log(cls.table, cls.idname, cls, where)
        return row

    @classmethod
    def copy(cls, id: int, loggging=True):
        from core.image import image
        row = cls.getById(id)

        if 'foto' in row:
            foto_copy = row['foto']
            del row['foto']
        else:
            foto_copy = None

        if 'archivo' in row:
            del row['archivo']

        fields     = table.getByname(cls.table)
        insert = database.create_data(fields, row)
        connection = database.instance()
        row = connection.insert(cls.table, cls.idname,
                                insert, cls.delete_cache)
        if isinstance(row, int) and row > 0:
            last_id = row
            if foto_copy != None:
                new_fotos = []
                for foto in foto_copy:
                    copiar = image.copy(
                        foto, last_id, foto['folder'], foto['subfolder'], last_id, '')
                    new_fotos.append(copiar['file'][0])
                    image.regenerar(copiar['file'][0])

                update = {'id': last_id, 'foto': json.dumps(new_fotos)}
                cls.update(update)

            if loggging:
                log.insert_log(cls.table, cls.idname, cls, insert)
                pass
            return last_id
        else:
            return row

    @classmethod
    def getByCookie(cls, cookie: str, estado_carro=True):
        where = {"cookie_pedido": cookie}
        if estado_carro:
            where['idpedidoestado'] = 1

        connection = database.instance()
        row = connection.get(cls.table, cls.idname, where)
        return row[0] if len(row) == 1 else row

    @classmethod
    def getByIdusuario(cls, idusuario: int, estado_carro=True):
        where = {"idusuario": idusuario}
        if estado_carro:
            where['idpedidoestado'] = 1
        condition = {'order': cls.idname + ' DESC'}
        connection = database.instance()
        row = connection.get(cls.table, cls.idname, where, condition)
        return row[0] if estado_carro and len(row) > 0 else row
