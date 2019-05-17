from core.app import app
from core.database import database
import json


class base_model:
    idname = ''
    table = ''

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
                if idpadre != None and str(idpadre) not in r['idpadre']:
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
    def getById(cls, id: int):
        from .table import table
        where = {cls.idname: id}
        if app.front:
            fields = table.getByname(cls.table)
            if 'estado' in fields:
                where['estado'] = True

        connection = database.instance()
        row = connection.get(cls.table, cls.idname, where)
        if len(row) == 1:
            if 'idpadre' in row[0]:
                if row[0]['idpadre'] != '':
                    row[0]['idpadre'] = json.loads(row[0]['idpadre'])
                else:
                    row[0]['idpadre'] = []
            if 'foto' in row[0]:
                if row[0]['foto'] != '':
                    row[0]['foto'] = json.loads(row[0]['foto'])
                else:
                    row[0]['foto'] = []
            if 'archivo' in row[0]:
                if row[0]['archivo'] != '':
                    row[0]['archivo'] = json.loads(row[0]['archivo'])
                else:
                    row[0]['archivo'] = []
        return row[0] if len(row) == 1 else row

    @classmethod
    def insert(cls, set_query: dict,  loggging=True):
        from .log import log
        from .table import table
        fields = table.getByname(cls.table)
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
        from .log import log
        where = {cls.idname: set_query['id']}
        del set_query['id']
        connection = database.instance()
        row = connection.update(cls.table, cls.idname, set_query, where)
        if loggging:
            log_register = set_query
            log_register.update(where)
            log.insert_log(cls.table, cls.idname, cls, log_register)
        if isinstance(row, bool) and row:
            row = where[cls.idname]
        return row

    @classmethod
    def delete(cls, id: int,logging=True):
        from .log import log
        where = {cls.idname: id}
        connection = database.instance()
        row = connection.delete(cls.table, cls.idname, where)
        if logging:
            log.insert_log(cls.table, cls.idname, cls, where)
        return row

    @classmethod
    def copy(cls, id: int, loggging=True):
        from .log import log
        from .table import table
        from core.image import image
        row = cls.getById(id)
        if 'idpadre' in row:
            row['idpadre'] = json.dumps(row['idpadre'])
        if 'foto' in row:
            foto_copy = row['foto']
            del row['foto']
        else:
            foto_copy = None

        if 'archivo' in row:
            archivo_copy = row['archivo']
            del row['archivo']
        else:
            archivo_copy = None

        fields = table.getByname(cls.table)
        insert = database.create_data(fields, row)
        connection = database.instance()
        row = connection.insert(cls.table, cls.idname, insert)
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

            if archivo_copy != None:
                new_archivos = []
                for archivo in archivo_copy:
                    copiar = image.copy(
                        archivo, last_id, archivo['folder'], archivo['subfolder'], last_id, '')
                    new_archivos.append(copiar['file'][0])
                update = {'id': last_id, 'archivo': json.dumps(new_archivos)}
                cls.update(update)

            if loggging:
                log.insert_log(cls.table, cls.idname, cls, insert)
                pass
            return last_id
        else:
            return row
