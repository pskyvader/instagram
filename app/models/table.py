from .base_model import base_model
from core.database import database
from core.app import app
import json


class table(base_model):
    idname = 'idtable'
    table = 'table'
    data = {
        "tablename": {"titulo": "tablename", "tipo": "char(255)"},
        "idname": {"titulo": "idname", "tipo": "char(255)"},
        "fields": {"titulo": "fields", "tipo": "longtext"},
        "truncate": {"titulo": "truncate", "tipo": "tinyint(1)"}
    }

    @classmethod
    def get_idname(cls):
        return cls.idname

    @classmethod
    def get_table(cls):
        return cls.table

    @classmethod
    def getAll(cls, where={}, condiciones={}, select=""):
        return_total = None
        connection = database.instance()
        if select == 'total':
            return_total = True

        row = connection.get(cls.table, cls.idname, where, condiciones, select)
        for r in row:
            if 'fields' in r:
                r['fields'] = json.loads(r['fields'])
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
            if 'fields' in row[0]:
                row[0]['fields'] = json.loads(row[0]['fields'])
        return row[0] if len(row) == 1 else row

    @classmethod
    def getByname(cls, name: str):
        if name == cls.table:
            return cls.data

        where = {'tablename': name}
        connection = database.instance()
        row = connection.get(cls.table, cls.idname, where)
        if len(row) == 1:
            if 'fields' in row[0]:
                row[0]['fields'] = json.loads(row[0]['fields'])
            fields = {}
            for field in row[0]['fields']:
                fields[field['titulo']] = field
            return fields
        else:
            print("No existe el modelo para la tabla" + name)
            return {}

    @classmethod
    def copy(cls, id: int, loggging=True):
        from .log import log
        row = cls.getById(id)
        row['fields'] = json.dumps(row['fields'])

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

    @classmethod
    def validate(cls, id: int, loggging=True):
        from .log import log
        config = app.get_config()
        respuesta = {"exito": True, "mensaje": []}
        table_validate = cls.getById(id)
        idname = table_validate['idname']
        tablename = table_validate['tablename']
        fields = list(table_validate['fields'])
        fields = [
            {'titulo': idname, 'tipo': 'int(11)', 'primary': True}]+fields

        check = {}
        for field in fields:
            if field['titulo'] not in check:
                check[field['titulo']] = field

                if 'primary' not in field:
                    field['primary'] = False

            else:
                respuesta['mensaje'] = 'Campo <b>"' + \
                    field['titulo'] + '"</b> Duplicado, Corregir.'
                respuesta['exito'] = False
                return respuesta

        existe = cls.table_exists(tablename)
        connection = database.instance()

        if existe:
            respuesta['mensaje'].append(
                'Tabla <b>"' + tablename + '"</b> existe')

            prefix = connection.get_prefix()
            connection.set_prefix('')

            table = 'information_schema.columns'
            where = {'table_schema': config["database"],
                 'table_name': prefix + tablename}
            condiciones = {}
            select = 'COLUMN_NAME,COLUMN_TYPE'
            row = connection.get(table, cls.idname, where, condiciones, select)

            connection.set_prefix(prefix)

            columns = {}
            for column in row:
                columns[column['COLUMN_NAME']] = column

            for key, field in enumerate(fields):
                field['after'] = fields[key - 1]['titulo'] if (key > 0) else ''

                if field['titulo'] in columns:
                    if columns[field['titulo']]['COLUMN_TYPE'] == field['tipo']:
                        respuesta['mensaje'].append(
                            'Columna <b>"' + field['titulo'] + '"</b> correcta')
                    else:
                        respuesta['mensaje'].append(
                            'Columna <b>"' + field['titulo'] + '"</b> incorrecta, Modificada')
                        respuesta['exito'] = connection.modify(
                            tablename, field['titulo'], field['tipo'])
                        if not respuesta['exito']:
                            respuesta['mensaje'].append(
                                'ERROR AL MODIFICAR campo ' + field['titulo'])
                            return respuesta

                else:
                    respuesta['mensaje'].append(
                        'Columna <b>"' + field['titulo'] + '"</b> No existe, Creada')
                    respuesta['exito'] = connection.add(
                        tablename, field['titulo'], field['tipo'], field['after'], field['primary'])
                    if not respuesta['exito']:
                        respuesta['mensaje'].append(
                            'ERROR AL AGREGAR CAMPO ' + field['titulo'])
                        return respuesta

        else:
            respuesta['mensaje'].append(
                'Tabla <b>"' + tablename + '"</b> No existe, Creada')
            respuesta['exito'] = connection.create(tablename, fields)
            if not respuesta['exito']:
                respuesta['mensaje'].append(
                    'ERROR AL CREAR TABLA ' + tablename)

        if loggging:
            log.insert_log(cls.table, cls.idname, cls, table_validate)
        return respuesta

    @classmethod
    def table_exists(cls, tablename: str):
        config = app.get_config()
        connection = database.instance()
        prefix = connection.get_prefix()
        connection.set_prefix('')
        table = 'information_schema.tables'
        where = {'table_schema': config["database"],
                 'table_name': prefix + tablename}
        condiciones = {}
        select = 'count(*) as count'
        row = connection.get(table, cls.idname, where, condiciones, select)
        connection.set_prefix(prefix)

        return (row[0]['count'] == 1)

    @classmethod
    def generar(cls, id: int):
        from pathlib import Path
        from core.view import view
        from .log import log
        import io
        config = app.get_config()
        respuesta = {'exito': True, 'mensaje': []}
        row = cls.getById(id)
        idname = row['idname']
        tablename = row['tablename']
        dir = app.get_dir(True)
        destino = dir + app.controller_dir + tablename + '.py'
        my_file = Path(destino)
        if my_file.is_file():
            respuesta['mensaje'].append(
                'Controlador ' + tablename + ' ya existe')
        else:
            controller_url = dir + 'app/templates/controllers/back/controller.tpl'
            controller_template = view.render_template(io.open(
                controller_url, encoding='utf-8').read(), {'name': tablename, 'theme': config['theme_back']})
            respuesta['mensaje'].append(
                'Controlador ' + tablename + ' no existe, creado')
            file_write = open(destino, 'w', encoding='utf-8')
            file_write.write(controller_template)
            file_write.close()

        destino = dir + 'app/models/' + tablename + '.py'
        my_file = Path(destino)
        if my_file.is_file():
            respuesta['mensaje'].append('Modelo ' + tablename + ' ya existe')
        else:
            model_url = dir + 'app/templates/models/back/model.tpl'
            model_template = view.render_template(io.open(
                model_url, encoding='utf-8').read(), {'class': tablename, 'table': tablename, 'idname': idname})

            respuesta['mensaje'].append(
                'Modelo ' + tablename + ' no existe, creado')
            file_write = open(destino, 'w', encoding='utf-8')
            file_write.write(model_template)
            file_write.close()

        log.insert_log(cls.table, cls.idname, cls, row)
        return respuesta

    @staticmethod
    def truncate(tables: list):
        from core.image import image
        respuesta = {'exito': True, 'mensaje': []}
        for table in tables:
            respuesta['mensaje'].append('Tabla ' + table + ' vaciada')
        connection = database.instance()
        respuesta['exito'] = connection.truncate(tables)
        if respuesta['exito']:
            for table in tables:
                image.delete(table)
        else:
            respuesta['mensaje'] = 'Error al vaciar tablas'
        return respuesta
