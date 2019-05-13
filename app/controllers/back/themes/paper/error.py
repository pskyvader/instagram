from .base import base

#from app.models.table import table as table_model
from app.models.administrador import administrador as administrador_model
#from app.models.modulo import modulo as modulo_model
#from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model

#from .detalle import detalle as detalle_class
#from .lista import lista as lista_class
from .head import head
from .header import header
from .aside import aside
from .footer import footer

#from core.app import app
#from core.database import database
from core.functions import functions
#from core.image import image


#import json

class error(base):
    url = ['error']
    metadata = {'title': 'error', 'modulo': 'error'}
    breadcrumb = []

    @classmethod
    def index(cls, var=[]):
        ret = {'body': []}
        url_final = cls.url.copy()
        if not administrador_model.verificar_sesion():
            url_final = ['login', 'index', 'home']
            url_return = functions.url_redirect(url_final)
            if url_return != '':
                ret['error'] = 301
                ret['redirect'] = url_return
                return ret

        h = head(cls.metadata)
        ret_head = h.normal()
        if ret_head['headers'] != '':
            return ret_head
        ret['body'] += ret_head['body']

        he = header()
        ret['body'] += he.normal()['body']

        asi = aside()
        ret['body'] += asi.normal()['body']
        data = {}
        if len(var) > 0:
            data['error'] = var[0]

        ret['body'].append(('404', data))

        f = footer()
        ret['body'] += f.normal()['body']

        return ret
