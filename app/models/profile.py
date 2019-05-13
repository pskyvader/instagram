from core.database import database
from .base_model import base_model


class profile(base_model):
    idname = 'idprofile'
    table = 'profile'
    @classmethod
    def getByTipo(cls, tipo: int):
        where = {'tipo': tipo, 'estado': True}
        condition = {'limit': 1}
        connection = database.instance()
        row = connection.get(cls.table, cls.idname, where, condition)
        return row[0] if len(row) == 1 else row
