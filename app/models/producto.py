from core.app import app
from core.database import database
from core.functions import functions
from .base_model import base_model
from .log import log
from .productocategoria import productocategoria
from .table import table
import json


class producto(base_model):
    idname = 'idproducto'
    table = 'producto'
    delete_cache = False

    @classmethod
    def getAll(cls, where={}, condiciones={}, select=""):
        limit = None
        idproductocategoria = None
        return_total = None
        connection = database.instance()
        fields = table.getByname(cls.table)
        if 'estado' not in where and app.front and 'estado' in fields:
            where['estado'] = True

        if 'idproductocategoria' in where:
            if 'idproductocategoria' in fields:
                idproductocategoria = where['idproductocategoria']
                if 'limit' in condiciones:
                    limit = condiciones['limit']
                    limit2 = 0
                    del condiciones['limit']

                if 'limit2' in condiciones:
                    if limit == None:
                        limit = 0
                    limit2 = condiciones['limit2']
                    del condiciones['limit2']
            del where['idproductocategoria']

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
            if idproductocategoria != None:
                select = ''

        row = connection.get(cls.table, cls.idname, where, condiciones, select)
        deleted = False
        row_copy = []
        for r in row:
            deleted = False
            if 'idproductocategoria' in r:
                r['idproductocategoria'] = json.loads(r['idproductocategoria'])
                if idproductocategoria != None and str(idproductocategoria) not in r['idproductocategoria']:
                    deleted = True

            if return_total == None:
                if not deleted and 'foto' in r and r['foto'] != '':
                    r['foto'] = json.loads(r['foto'])
                else:
                    r['foto'] = []

                if not deleted and 'archivo' in r and r['archivo'] != '':
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
            if idproductocategoria != None:
                return len(row)
            else:
                return row[0]['total']
        else:
            variables = {}
            if 'tipo' in where:
                variables['tipo'] = where['tipo']
            cat = productocategoria.getAll(variables)
            categorias = {}
            for c in cat:
                categorias[c[0]] = {'descuento': c['descuento'],
                                    'descuento_fecha': c['descuento_fecha']}

            for v in row:
                if 'precio' in v:
                    v['idproductocategoria'][0] = int(
                        v['idproductocategoria'][0])
                    v['precio_final'] = v['precio']
                    descuento = 0
                    if v['descuento'] != 0:
                        descuento = v['descuento']
                        fechas = v['descuento_fecha']
                    elif len(v['idproductocategoria']) > 0 and v['idproductocategoria'][0] in categorias and categorias[v['idproductocategoria'][0]]['descuento'] != 0:

                        descuento = categorias[v['idproductocategoria']
                                               [0]]['descuento']
                        fechas = categorias[v['idproductocategoria']
                                            [0]]['descuento_fecha']
                    if descuento > 0 and descuento < 100:
                        fechas = fechas.split(' - ')
                        fecha1 = functions.formato_fecha(
                            fechas[0], original_format="%d/%m/%Y %H:%M", as_string=False)
                        fecha2 = functions.formato_fecha(
                            fechas[1], original_format="%d/%m/%Y %H:%M", as_string=False)
                        now = functions.current_time(as_string=False)
                        if fecha1 < now and now < fecha2:
                            precio_descuento = (
                                (v['precio']) * descuento) / 100
                            precio_final = v['precio'] - precio_descuento
                            if precio_final < 1:
                                precio_final = 1
                            v['precio_final'] = int(precio_final)
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
            row[0]['idproductocategoria'] = json.loads(
                row[0]['idproductocategoria'])
            if 'foto' in row[0] and row[0]['foto'] != '':
                row[0]['foto'] = json.loads(row[0]['foto'])
            else:
                row[0]['foto'] = []
            if 'archivo' in row[0] and row[0]['archivo'] != '':
                row[0]['archivo'] = json.loads(row[0]['archivo'])
            else:
                row[0]['archivo'] = []

            if 'precio' in row[0]:
                cat = productocategoria.getById(
                    row[0]['idproductocategoria'][0])
                categorias = {}
                if len(cat) > 0:
                    categorias[cat[0]] = {
                        'descuento': cat['descuento'], 'descuento_fecha': cat['descuento_fecha']}

                row[0]['precio_final'] = row[0]['precio']
                descuento = 0
                if row[0]['descuento'] != 0:
                    descuento = row[0]['descuento']
                    fechas = row[0]['descuento_fecha']
                elif row[0]['idproductocategoria'][0] in categorias and categorias[row[0]['idproductocategoria'][0]]['descuento'] != 0:
                    descuento = categorias[row[0]
                                           ['idproductocategoria'][0]]['descuento']
                    fechas = categorias[row[0]
                                        ['idproductocategoria'][0]]['descuento_fecha']

                if descuento > 0 and descuento < 100:
                    fechas = fechas.split(' - ')
                    fecha1 = functions.formato_fecha(
                        fechas[0], original_format="%d/%m/%Y %H:%M", as_string=False)
                    fecha2 = functions.formato_fecha(
                        fechas[1], original_format="%d/%m/%Y %H:%M", as_string=False)
                    now = functions.current_time(as_string=False)
                    if fecha1 < now and now < fecha2:
                        precio_descuento = (
                            (row[0]['precio']) * descuento) / 100
                        precio_final = row[0]['precio'] - precio_descuento
                        if precio_final < 1:
                            precio_final = 1
                        row[0]['precio_final'] = int(precio_final)

        return row[0] if len(row) == 1 else row

    @classmethod
    def update(cls, set_query: dict, loggging=True):
        where = {cls.idname: set_query['id']}
        del set_query['id']
        connection = database.instance()
        if app.front:
            row = connection.update(
                cls.table, cls.idname, set_query, where, cls.delete_cache)
        else:
            row = connection.update(cls.table, cls.idname, set_query, where)

        if loggging:
            log_register = set_query
            log_register.update(where)
            log.insert_log(cls.table, cls.idname, cls, log_register)
        if isinstance(row, bool) and row:
            row = where[cls.idname]
        return row

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
            archivo_copy = row['archivo']
            del row['archivo']
        else:
            archivo_copy = None

        row['idproductocategoria'] = json.dumps(row['idproductocategoria'])
        fields = table.getByname(cls.table)
        insert = database.create_data(fields, row)
        connection = database.instance()
        row = connection.insert(cls.table, cls.idname, insert)
        if isinstance(row, int) and row > 0:
            last_id = row

            if foto_copy != None:
                new_fotos = []
                for foto in foto_copy:
                    copiar = image.copy(foto, foto['id'], foto['folder'], foto['subfolder'], last_id, '')
                    new_fotos.append(copiar['file'][0])
                    image.regenerar(copiar['file'][0])

                update = {'id': last_id, 'foto': json.dumps(new_fotos)}
                cls.update(update)

            if archivo_copy != None:
                new_archivos = []
                for archivo in archivo_copy:
                    name_final=archivo['url'].split('.')
                    name_final.pop()
                    name_final='.'.join(name_final)

                    copiar = image.copy( archivo, name_final, archivo['folder'], archivo['subfolder'], last_id, '')
                    new_archivos.append(copiar['file'][0])
                update = {'id': last_id, 'archivo': json.dumps(new_archivos)}
                cls.update(update)

            if loggging:
                log.insert_log(cls.table, cls.idname, cls, (insert))
                pass
            return last_id
        else:
            return row
