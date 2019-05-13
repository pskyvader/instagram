from .base_model import base_model
from core.database import database
from core.app import app
from .table import table
import json


class seccion(base_model):
    idname = 'idseccion'
    table = 'seccion'

    @classmethod
    def getAll(cls, where={}, condiciones={}, select=""):
        limit = None
        idseccioncategoria = None
        return_total = None
        connection = database.instance()
        fields = table.getByname(cls.table)
        if 'estado' not in where and app.front and 'estado' in fields:
            where['estado'] = True

        if 'idseccioncategoria' in where:
            if 'idseccioncategoria' in fields:
                idseccioncategoria = where['idseccioncategoria']
                if 'limit' in condiciones:
                    limit = condiciones['limit']
                    limit2 = 0
                    del condiciones['limit']

                if 'limit2' in condiciones:
                    if limit == None:
                        limit = 0
                    limit2 = condiciones['limit2']
                    del condiciones['limit2']
            del where['idseccioncategoria']

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
            if idseccioncategoria != None:
                select = ''

        row = connection.get(cls.table, cls.idname, where, condiciones, select)
        deleted = False
        row_copy = []
        for r in row:
            deleted = False
            if 'idseccioncategoria' in r and r['idseccioncategoria']!='':
                r['idseccioncategoria'] = json.loads(r['idseccioncategoria'])
                if idseccioncategoria != None and idseccioncategoria not in r['idseccioncategoria']:
                    deleted = True

            if return_total == None:
                if not deleted and 'foto' in r and r['foto'] != '':
                    r['foto'] = json.loads(r['foto'])

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
            if idseccioncategoria != None:
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
            row[0]['idseccioncategoria'] = json.loads(
                row[0]['idseccioncategoria'])
            if 'foto' in row[0] and row[0]['foto'] != '':
                row[0]['foto'] = json.loads(row[0]['foto'])
            if 'archivo' in row[0] and row[0]['archivo'] != '':
                row[0]['archivo'] = json.loads(row[0]['archivo'])
        return row[0] if len(row) == 1 else row

    @classmethod
    def copy(cls, id: int, loggging=True):
        from .log import log
        from core.image import image
        row = cls.getById(id)

        if 'foto' in row:
            foto_copy = row['foto']
            del row['foto']
        else:
            foto_copy = None

        if 'archivo' in row:
            del row['archivo']
        
        row['idseccioncategoria'] = json.dumps(row['idseccioncategoria'])
        fields = table.getByname(cls.table)
        insert = database.create_data(fields, row)
        connection = database.instance()
        row = connection.insert(cls.table, cls.idname, insert)
        if isinstance(row, int) and row > 0:
            last_id = row
            if foto_copy != None:
                new_fotos = []
                for foto in foto_copy:
                    copiar = image.copy( foto, last_id, foto['folder'], foto['subfolder'], last_id, '')
                    new_fotos.append(copiar['file'][0])
                    image.regenerar(copiar['file'][0])

                update = {'id': last_id, 'foto': json.dumps(new_fotos)}
                cls.update(update)

            if loggging:
                log.insert_log(cls.table, cls.idname, cls, (insert))
                pass
            return last_id
        else:
            return row
