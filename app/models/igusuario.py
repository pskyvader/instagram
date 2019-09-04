from .base_model import base_model
#from core.app import app
from core.database import database
from .log import log
#from .productocategoria import productocategoria
#from .table import table
#import datetime
#import json

from .base_model import base_model


class igusuario(base_model):
    idname = 'idigusuario'
    table = 'igusuario'

    @classmethod
    def update(cls, set_query: dict, loggging=True):
        if "pass" in set_query and set_query["pass"] != "":
            if "pass_repetir" in set_query and set_query["pass_repetir"] != "":
                if set_query["pass"] != set_query["pass_repetir"]:
                    return {"exito": False, "mensaje": "Contraseñas no coinciden"}
                else:
                    del set_query["pass_repetir"]
            else:
                return {"exito": False, "mensaje": "Contraseña no existe"}
        else:
            if "pass" in set_query:
                del set_query["pass"]
            if "pass_repetir" in set_query:
                del set_query["pass_repetir"]

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