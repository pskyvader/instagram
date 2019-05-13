from .base_model import base_model
from core.database import database
from core.app import app
from .table import table
import json


class seo(base_model):
    idname = 'idseo'
    table = 'seo'

    @classmethod
    def getAll(cls, where={}, condiciones={}, select=""):
        limit = None
        idpadre = None
        return_total = None
        connection = database.instance()
        fields = table.getByname(cls.table)
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
                r['idpadre'] = json.loads(r['idpadre'])
                if idpadre != None and idpadre not in r['idpadre']:
                    deleted = True

            if return_total == None:
                if not deleted and 'foto' in r and r['foto'] != '':
                    r['foto'] = json.loads(r['foto'])
                if not deleted and 'banner' in r and r['banner'] != '':
                    r['banner'] = json.loads(r['banner'])
                if not deleted and 'archivo' in r and r['archivo'] != '':
                    r['archivo'] = json.loads(r['archivo'])

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
        where = {cls.idname: id}
        if app.front:
            fields = table.getByname(cls.table)
            if 'estado' in fields:
                where['estado'] = True

        connection = database.instance()
        row = connection.get(cls.table, cls.idname, where)
        if len(row) == 1:
            if 'idpadre' in row[0] and row[0]['idpadre']!='':
                row[0]['idpadre'] = json.loads(row[0]['idpadre'])
            if 'foto' in row[0] and row[0]['foto']!='':
                row[0]['foto'] = json.loads(row[0]['foto'])
            if 'banner' in row[0] and row[0]['banner']!='':
                row[0]['banner'] = json.loads(row[0]['banner'])
            if 'archivo' in row[0] and row[0]['archivo']!='':
                row[0]['archivo'] = json.loads(row[0]['archivo'])
        return row[0] if len(row) == 1 else row

    @classmethod
    def copy(cls, id: int, loggging=True):
        from .log import log
        from core.image import image
        row = cls.getById(id)
        if 'idpadre' in row:
            row['idpadre'] = json.dumps(row['idpadre'])
        if 'foto' in row:
            foto_copy = row['foto']
            del row['foto']
        else:
            foto_copy = None
        if 'banner' in row:
            banner_copy = row['banner']
            del row['banner']
        else:
            banner_copy = None

        if 'archivo' in row:
            del row['archivo']

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

            if banner_copy != None:
                new_banners = []
                for banner in banner_copy:
                    copiar = image.copy(
                        banner, last_id, banner['folder'], banner['subfolder'], last_id, '')
                    new_banners.append(copiar['file'][0])
                    image.regenerar(copiar['file'][0])

                update = {'id': last_id, 'banner': json.dumps(new_banners)}
                cls.update(update)

            if loggging:
                log.insert_log(cls.table, cls.idname, cls, (insert))
                pass
            return last_id
        else:
            return row
