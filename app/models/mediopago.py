from core.database import database
from .base_model import base_model


class mediopago(base_model):
    idname = 'idmediopago'
    table = 'mediopago'
    @classmethod
    def getById(cls, id: int):
        where = {cls.idname: id}
        connection = database.instance()
        row = connection.get(cls.table, cls.idname, where)
        return row[0] if len(row) == 1 else row
