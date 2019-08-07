from core.database import database
from .base_model import base_model
import ast
import json


class configuracion(base_model):
    idname = "idconfiguracion"
    table = "configuracion"

    @classmethod
    def getByVariable(cls, variable: str, default=None):
        where = {"variable": variable}
        condicion = {"limit": 1}
        connection = database.instance()
        row = connection.get(cls.table, cls.idname, where, condicion)
        if len(row) == 1:
            ret=None
            try:
                ret=ast.literal_eval(row[0]["valor"])
            except Exception as e:
                if default!=None and isinstance(row[0]["valor"],type(default)):
                    ret=row[0]["valor"]
                else:
                    print('error al convertir variable', e,row[0]["valor"])
                    ret=default

            return ret
        else:
            if default == None:
                return False
            else:
                configuracion.setByVariable(variable, default)
                return default

    @classmethod
    def setByVariable(cls, variable: str, valor: str, logging=True):
        where = {"variable": variable}
        condicion = {"limit": 1}
        connection = database.instance()
        row = connection.get(cls.table, cls.idname, where, condicion)
        if isinstance(valor, dict) or isinstance(valor, list):
            valor = json.dumps(valor)

        if len(row) == 0:
            row = cls.insert({"variable": variable, "valor": valor}, logging)
        else:
            row = cls.update(
                {"variable": variable, "valor": valor, "id": row[0][0]}, logging
            )

        return row
