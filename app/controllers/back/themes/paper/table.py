from .base import base
from app.models.table import table as table_model

#from app.models.table import table as table_model
from app.models.administrador import administrador as administrador_model
#from app.models.modulo import modulo as modulo_model
#from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model

from .detalle import detalle as detalle_class
from .lista import lista as lista_class
#from .head import head
#from .header import header
#from .aside import aside
#from .footer import footer

from core.app import app
#from core.database import database
from core.functions import functions
#from core.image import image

import json


class table(base):
    url = ['table']
    metadata = {'title': 'Tablas', 'modulo': 'table'}
    breadcrumb = []
    tipos = {
        'char(255)': {'text': 'Texto', 'value': 'char(255)'},
        'int(11)': {'text': 'Numero', 'value': 'int(11)'},
        'tinyint(1)': {'text': 'Bool', 'value': 'tinyint(1)'},
        'longtext': {'text': 'Texto largo', 'value': 'longtext'},
        'datetime': {'text': 'Fecha y hora', 'value': 'datetime'},
    }

    def __init__(self):
        super().__init__(table_model)

    @classmethod
    def index(cls):
        '''Controlador de lista_class de elementos base, puede ser sobreescrito en el controlador de cada modulo'''
        ret = {'body': ''}
        # Clase para enviar a controlador de lista_class
        class_name = cls.class_name
        url_final = cls.url.copy()

        if not administrador_model.verificar_sesion():
            url_final = ['login', 'index'] + url_final
        # verificar sesion o redireccionar a login
        url_return = functions.url_redirect(url_final)
        if url_return != '':
            ret['error'] = 301
            ret['redirect'] = url_return
            return ret

        # cabeceras y campos que se muestran en la lista_class:
        # titulo,campo de la tabla a usar, tipo (ver archivo lista_class.py funcion "field")
        th = {
            'id': {'title_th': 'ID', 'field': 0, 'type': 'text'},
            'tablename': {'title_th': 'Titulo', 'field': 'tablename', 'type': 'text'},
            'truncate': {'title_th': 'Permite vaciar', 'field': 'truncate', 'type': 'active'},
            'validar': {'title_th': 'Validar', 'field': 0, 'type': 'action', 'action': 'validar', 'mensaje': 'Validando Tabla'},
            'generar': {'title_th': 'Generar mvc', 'field': 0, 'type': 'action', 'action': 'generar', 'mensaje': 'Generando mvc'},
            'copy': {'title_th': 'Copiar', 'field': 0, 'type': 'action', 'action': 'copy', 'mensaje': 'Copiando Elemento'},
            'editar': {'title_th': 'Editar', 'field': 'url_detalle', 'type': 'link'},
        }

        # controlador de lista_class
        lista = lista_class(cls.metadata)
        head=lista.head()
        if head!=False:
            return head
        where = {}
        condiciones = {}
        url_detalle = url_final.copy()
        url_detalle.append('detail')
        # obtener unicamente elementos de la pagina actual
        respuesta = lista.get_row(class_name, where, condiciones, url_detalle)

        menu = {'new': True, 'regenerar': False, 'excel': False}

        # informacion para generar la vista de lista_class
        data = {
            'breadcrumb': cls.breadcrumb,
            'th': th,
            'current_url': functions.generar_url(url_final),
            'new_url': functions.generar_url(url_detalle),
        }

        data.update(respuesta)
        data.update(menu)
        ret = lista.normal(data)
        return ret

    @classmethod
    def detail(cls, var=[]):
        '''Controlador de detalle de elementos base, puede ser sobreescrito en el controlador de cada modulo'''
        ret = {'body': ''}
        # Clase para enviar a controlador de detalle
        class_name = cls.class_name
        url_list = cls.url.copy()
        url_save = cls.url.copy()
        url_final = cls.url.copy()
        metadata = cls.metadata.copy()
        url_save.append('guardar')
        url_final.append('detail')
        if len(var) > 0:
            id = int(var[0])
            url_final.append(id)
            metadata['title'] = 'Editar ' + metadata['title']
        else:
            id = 0
            metadata['title'] = 'Nuevo ' + metadata['title']

        cls.breadcrumb.append({'url': functions.generar_url(
            url_final), 'title': metadata['title'], 'active': 'active'})

        if not administrador_model.verificar_sesion():
            url_final = ['login', 'index'] + url_final
        # verificar sesion o redireccionar a login
        url_return = functions.url_redirect(url_final)
        if url_return != '':
            ret['error'] = 301
            ret['redirect'] = url_return
            return ret

        # cabeceras y campos que se muestran en el detalle:
        # titulo,campo de la tabla a usar, tipo (ver archivo detalle.py funcion "field")

        columnas = {
            'orden': {'title_field': 'Orden', 'field': 'orden', 'type': 'multiple_order', 'required': True, 'col': 2},
            'titulo': {'title_field': 'Titulo', 'field': 'titulo', 'type': 'multiple_text', 'required': True, 'col': 3},
            'tipo': {'title_field': 'Tipo', 'field': 'tipo', 'type': 'multiple_select', 'required': True, 'option': cls.tipos, 'col': 3},
            'button': {'field': '', 'type': 'multiple_button', 'col': 4},
        }
        campos = {
            'tablename': {'title_field': 'Titulo', 'field': 'tablename', 'type': 'text', 'required': True},
            'idname': {'title_field': 'ID tablas', 'field': 'idname', 'type': 'text', 'required': True},
            'fields': {'title_field': 'Campos', 'field': 'fields', 'type': 'multiple', 'required': True, 'columnas': columnas},
            'truncate': {'title_field': 'Permite vaciar', 'field': 'truncate', 'type': 'active', 'required': True},
        }

        # controlador de detalle
        detalle = detalle_class(metadata)
        row = class_name.getById(id) if id != 0 else []

        # informacion para generar la vista del detalle
        data = {
            'breadcrumb': cls.breadcrumb,
            'campos': campos,
            'row': row,
            'id': id if id != 0 else '',
            'current_url': functions.generar_url(url_final),
            'save_url': functions.generar_url(url_save),
            'list_url': functions.generar_url(url_list),
        }

        ret = detalle.normal(data)
        return ret

    def validar(self):
        ret = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        campos = app.post['campos']
        class_name = self.class_name
        respuesta = class_name.validate(campos['id'])
        ret['body'] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    def generar(self):
        ret = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        campos = app.post['campos']
        class_name = self.class_name
        respuesta = class_name.generar(campos['id'])
        ret['body'] = json.dumps(respuesta, ensure_ascii=False)
        return ret
