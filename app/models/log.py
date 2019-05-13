from core.app import app
from core.database import database
from core.functions import functions
from .base_model import base_model
from .table import table


class log(base_model):
    idname = 'idlog'
    table = 'log'
    delete_cache = False
    @classmethod
    def insert(cls, set_query: dict,  loggging=True):
        fields     = table.getByname(cls.table)
        insert = database.create_data(fields, set_query)
        connection = database.instance()
        row = connection.insert(cls.table, cls.idname, insert, cls.delete_cache)
        if isinstance(row, int) and row > 0:
            last_id = row
            if loggging:
                log.insert_log(cls.table, cls.idname, cls, insert)
                pass
            return last_id
        else:
            return row

    @classmethod
    def insert_log(cls, tabla: str, idname: str, funcion, row: dict):
        if tabla != cls.table and not app.front:
            if 'nombre' + app.prefix_site in app.session:
                administrador = app.session['nombre' + app.prefix_site] +  ' (' + app.session['email' + app.prefix_site] + ')'
            else:
                administrador=''
            accion = 'metodo: ' + funcion.__name__
            if 'titulo' in row:
                accion += ', titulo: ' + row['titulo']
            elif 'nombre' in row:
                accion += ', nombre: ' + row['nombre']
            elif 'tablename' in row:
                accion += ', Tabla: ' + row['tablename']

            if idname in row:
                accion += ', ID: ' + str(row[idname])
            elif 'id' in row:
                accion += ', ID: ' + str(row['id'])

            data = {
                'administrador': administrador,
                'tabla': tabla,
                'accion': accion,
                'fecha': functions.current_time(),
            }
            cls.insert(data)
