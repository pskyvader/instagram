from core.database import database
from .base_model import base_model
from .log import log
from .table import table
import json
import ast


class modulo(base_model):
    idname = 'idmodulo'
    table = 'modulo'
    @classmethod
    def getAll(cls, where={}, condiciones={}, select=""):
        return_total = None
        connection = database.instance()
        fields = table.getByname(cls.table)

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
        for r in row:
            if 'menu' in r and r['menu'] != '':
                r['menu'] = json.loads(r['menu'])
            else:
                r['menu'] = []
            if 'mostrar' in r and r['mostrar'] != '':
                r['mostrar'] = json.loads(r['mostrar'])
            else:
                r['mostrar'] = []
            if 'detalle' in r and r['detalle'] != '':
                r['detalle'] = json.loads(r['detalle'])
            else:
                r['detalle'] = []
            if 'recortes' in r and r['recortes'] != '':
                r['recortes'] = json.loads(r['recortes'])
            else:
                r['recortes'] = []

            if 'estado' in r and r['estado'] != '':
                r['estado'] =ast.literal_eval(r['estado'])
                #r['estado'] = json.loads(r['estado'])
            else:
                r['estado'] = []

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
            if 'menu' in row[0] and row[0]['menu'] != '':
                row[0]['menu'] = json.loads(row[0]['menu'])
            else:
                row[0]['menu'] = []
            if 'mostrar' in row[0] and row[0]['mostrar'] != '':
                row[0]['mostrar'] = json.loads(row[0]['mostrar'])
            else:
                row[0]['mostrar'] = []

            if 'detalle' in row[0] and row[0]['detalle'] != '':
                row[0]['detalle'] = json.loads(row[0]['detalle'])
            else:
                row[0]['detalle'] = []

            if 'recortes' in row[0] and row[0]['recortes'] != '':
                row[0]['recortes'] = json.loads(row[0]['recortes'])
            else:
                row[0]['recortes'] = []
            if 'estado' in row[0] and row[0]['estado'] != '':
                row[0]['estado'] = ast.literal_eval(row[0]['estado'])
                #row[0]['estado'] = json.loads(row[0]['estado'])
            else:
                row[0]['estado'] = []

        return row[0] if len(row) == 1 else row

    @classmethod
    def copy(cls, id: int, loggging=True):
        row = cls.getById(id)
        row['menu'] = json.dumps(row['menu'],ensure_ascii=False)
        row['mostrar'] = json.dumps(row['mostrar'],ensure_ascii=False)
        row['detalle'] = json.dumps(row['detalle'],ensure_ascii=False)
        row['recortes'] = json.dumps(row['recortes'],ensure_ascii=False)
        row['estado'] = json.dumps(row['estado'],ensure_ascii=False)

        fields = table.getByname(cls.table)
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
