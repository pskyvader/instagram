from .base import base
from app.models.administrador import administrador as administrador_model


from app.models.logo import logo as logo_model

from .head import head
from .footer import footer

from core.app import app
from core.functions import functions
from core.image import image


class application(base):
    url = ['home']
    metadata = {'title': 'home', 'modulo': 'home'}
    breadcrumb = []

    @classmethod
    def index(cls):
        '''Controlador de lista_class de elementos base, puede ser sobreescrito en el controlador de cada modulo'''
        ret = {'body': []}
        # Clase para enviar a controlador de lista_class
        url_final = cls.url.copy()
        if not administrador_model.verificar_sesion():
            url_final = ['login', 'index', 'home']

        h = head(cls.metadata)
        ret_head = h.normal()
        if ret_head['headers'] != '':
            return ret_head
        ret['body'] += ret_head['body']

        config = app.get_config()
        logo = logo_model.getById(7)
        portada=image.portada(logo['foto'])
        data = {}
        data['color_primario'] = config['color_primario']
        data['color_secundario'] = config['color_secundario']
        data['logo'] = image.generar_url(portada, 'icono600')
        data['path'] = functions.generar_url(url_final)

        ret['body'].append(('application', data))

        f = footer()
        ret['body'] += f.normal()['body']

        return ret
