from .base_model import base_model
from core.database import database


class sitemap(base_model):
    idname = 'idsitemap'
    table = 'sitemap'

    @classmethod
    def getAll(cls, where={}, condiciones={}, select=""):
        return_total = None
        connection = database.instance()
        if select == 'total':
            return_total = True

        row = connection.get(cls.table, cls.idname, where, condiciones, select)

        if return_total != None:
            return row[0]['total']
        else:
            return row

    @classmethod
    def truncate(cls):
        respuesta = {'exito': True, 'mensaje': []}
        connection = database.instance()
        respuesta['exito'] = connection.truncate([cls.table])
        if not respuesta['exito']:
            respuesta['mensaje'] = 'Error al vaciar tablas'
        return respuesta
