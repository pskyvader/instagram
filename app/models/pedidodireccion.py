from core.database import database
from .base_model import base_model
from .log import log
from .table import table
import json


class pedidodireccion(base_model):
    idname = 'idpedidodireccion'
    table = 'pedidodireccion'
    delete_cache = False



    @classmethod
    def insert(cls, set_query: dict,  loggging=True):
        fields     = table.getByname(cls.table)
        insert = database.create_data(fields, set_query)
        connection = database.instance()
        row = connection.insert(cls.table, cls.idname, insert,cls.delete_cache)
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
        row = connection.update(cls.table, cls.idname, set_query, where,cls.delete_cache)
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
        row = connection.delete(cls.table, cls.idname, where,cls.delete_cache)
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
        row = connection.insert(cls.table, cls.idname, insert,cls.delete_cache)
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
