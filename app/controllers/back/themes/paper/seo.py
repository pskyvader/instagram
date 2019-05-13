from .base import base
from app.models.seo import seo as seo_model

#from app.models.table import table as table_model
#from app.models.administrador import administrador as administrador_model
#from app.models.modulo import modulo as modulo_model
#from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model

#from .detalle import detalle as detalle_class
#from .lista import lista as lista_class
#from .head import head
#from .header import header
#from .aside import aside
#from .footer import footer

from core.app import app
#from core.database import database
#from core.functions import functions
#from core.image import image

import json


class seo(base):
    url = ['seo']
    metadata = {'title': 'seo', 'modulo': 'seo'}
    breadcrumb = []

    def __init__(self):
        super().__init__(seo_model)

    @classmethod
    def get_all(cls):
        get = app.get
        respuesta = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        respuesta['body'] = {'exito': False,
                             'mensaje': 'Debes recargar la pagina'}
        if cls.contiene_tipos and 'tipo' not in get:
            respuesta['body'] = json.dumps(
                respuesta['body'], ensure_ascii=False)
            return

        if cls.contiene_hijos and 'idpadre' not in get:
            respuesta['body'] = json.dumps(
                respuesta['body'], ensure_ascii=False)
            return

        where = {}
        if cls.contiene_tipos:
            where['tipo'] = get['tipo']

        if cls.contiene_hijos:
            where['idpadre'] = get['idpadre']

        if cls.class_parent != None:
            class_parent = cls.class_parent
            if class_parent.idname in get:
                where[class_parent.idname] = get[class_parent.idname]

        condiciones = {}
        select = ""
        class_name = cls.class_name
        row = class_name.getAll(where, condiciones, select)

        for key in range(len(row)):
            row[key]['foto'] = row[key]['foto']+row[key]['banner']

        respuesta['body'] = json.dumps(row, ensure_ascii=False)
        return respuesta
