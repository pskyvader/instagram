from core.app import app
from core.database import database
from .base_model import base_model
from .log import log
from .table import table
import json


class moduloconfiguracion(base_model):
    idname = 'idmoduloconfiguracion'
    table = 'moduloconfiguracion'

    @classmethod
    def getAll(cls, where={}, condiciones={}, select=""):
        return_total = None
        connection = database.instance()
        fields     = table.getByname(cls.table)
        if 'estado' not in where and app.front and 'estado' in fields:
            where['estado'] = True

        if 'order' not in condiciones and 'orden' in fields:
            condiciones['order'] = 'orden ASC'

        if 'palabra' in condiciones:
            condiciones['buscar'] = {}
            if 'titulo' in fields:
                condiciones['buscar']['titulo'] = condiciones['palabra']

            if len(condiciones['buscar']) == 0:
                del condiciones['buscar']

        if select == 'total':
            return_total = True

        row = connection.get(cls.table, cls.idname, where, condiciones, select)
        if return_total == None:
            for r in row:
                if 'mostrar' in r and r['mostrar']!='':
                    r['mostrar'] = json.loads(r['mostrar'])
                else:
                    r['mostrar']=[]
                if 'detalle' in r and r['detalle']!='':
                    r['detalle'] = json.loads(r['detalle'])
                else:
                    r['detalle']=[]

        if return_total != None:
            return row[0]['total']
        else:
            return row

    @classmethod
    def getById(cls, id: int):
        where = {cls.idname: id}

        connection = database.instance()
        row = connection.get(cls.table, cls.idname, where)
        if len(row) == 1:
            if 'mostrar' in row[0] and row[0]['mostrar']!='':
                row[0]['mostrar'] = json.loads(row[0]['mostrar'])
            else:
                row[0]['mostrar'] = []
            if 'detalle' in row[0] and row[0]['detalle']!='':
                row[0]['detalle'] = json.loads(row[0]['detalle'])
            else:
                row[0]['detalle'] = []
        return row[0] if len(row) == 1 else row

    @classmethod
    def getByModulo(cls, modulo: str):
        where = {'module': modulo}
        connection = database.instance()
        row = connection.get(cls.table, cls.idname, where)
        if len(row) == 1:
            if 'mostrar' in row[0] and row[0]['mostrar']!='':
                row[0]['mostrar'] = json.loads(row[0]['mostrar'])
            else:
                row[0]['mostrar'] = []
            if 'detalle' in row[0] and row[0]['detalle']!='':
                row[0]['detalle'] = json.loads(row[0]['detalle'])
            else:
                row[0]['detalle'] = []
        return row[0] if len(row) == 1 else row

    @classmethod
    def copy(cls, id: int, loggging=True):
        from core.image import image
        row = cls.getById(id)

        row['mostrar'] = json.dumps(row['mostrar'],ensure_ascii=False)
        row['detalle'] = json.dumps(row['detalle'],ensure_ascii=False)

        fields     = table.getByname(cls.table)
        insert = database.create_data(fields, row)
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
