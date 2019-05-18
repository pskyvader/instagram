from .base import base
from app.models.administrador import administrador as administrador_model

from app.models.table import table
from core.app import app
from core.functions import functions

from .detalle import detalle as detalle_class


import json


class administrador(base):
    url = ['administrador']
    metadata = {'title': 'administrador', 'modulo': 'administrador'}
    breadcrumb = []

    def __init__(self):
        super().__init__(administrador_model)

    @classmethod
    def detail(cls, var=[]):
        '''Controlador de detalle de elementos base, puede ser sobreescrito en el controlador de cada modulo'''
        ret = {'body': ''}
        # Clase para enviar a controlador de detalle
        class_name = cls.class_name
        get = app.get
        url_list = cls.url.copy()
        url_save = cls.url.copy()
        url_final = cls.url.copy()
        url_save.append('guardar')
        url_final.append('detail')
        if len(var) > 0:
            id = int(var[0])
            url_final.append(id)
            cls.metadata['title'] = 'Editar ' + cls.metadata['title']
        else:
            id = 0
            cls.metadata['title'] = 'Nuevo ' + cls.metadata['title']

        cls.breadcrumb.append({'url': functions.generar_url(
            url_final), 'title': cls.metadata['title'], 'active': 'active'})
        if cls.contiene_tipos and 'tipo' not in get:
            url_final = ['home']

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

        # controlador de detalle
        detalle = detalle_class(cls.metadata)
        configuracion = detalle.configuracion(cls.metadata['modulo'])

        if 'error' in configuracion:
            ret['error'] = configuracion['error']
            ret['redirect'] = configuracion['redirect']
            return ret

        row = class_name.getById(id) if id != 0 else {}
        if cls.contiene_tipos:
            configuracion['campos']['tipo'] = {
                'title_field': 'tipo', 'field': 'tipo', 'type': 'hidden', 'required': True}
            row['tipo'] = get['tipo']

        if cls.contiene_hijos and 'idpadre' in configuracion['campos']:
            categorias = class_name.getAll()
            for c in categorias:
                if c[0] == id:
                    del c
                    break

            raiz = {0: 0, 'titulo': 'Raíz', 'idpadre': [-1]}
            categorias = raiz+categorias
            configuracion['campos']['idpadre']['parent'] = functions.crear_arbol(
                categorias, -1)
        elif cls.contiene_hijos or 'idpadre' in configuracion['campos']:
            configuracion['campos']['idpadre'] = {
                'title_field': 'idpadre', 'field': 'idpadre', 'type': 'hidden', 'required': True}
            if id == 0:
                if 'idpadre' in get:
                    row['idpadre'] = json.dumps([get['idpadre']])
                else:
                    row['idpadre'] = json.dumps([0])
        else:
            if 'idpadre' in configuracion['campos']:
                del configuracion['campos']['idpadre']

        if cls.class_parent != None:
            class_parent = cls.class_parent
            idparent = class_parent.idname

            is_array = True
            fields = table.getByname(class_name.table)
            if idparent in fields and fields[idparent]['tipo'] != 'longtext':
                is_array = False

            if idparent in configuracion['campos']:
                categorias = class_parent.getAll()
                if is_array:
                    configuracion['campos'][idparent]['parent'] = functions.crear_arbol(
                        categorias)
                else:
                    configuracion['campos'][idparent]['parent'] = categorias

            else:
                configuracion['campos'][idparent] = {
                    'title_field': idparent, 'field': idparent, 'type': 'hidden', 'required': True}
                if id == 0:
                    if idparent in get:
                        if is_array:
                            row[idparent] = json.dumps([get[idparent]])
                        else:
                            row[idparent] = int(get[idparent])
                    else:
                        if is_array:
                            row[idparent] = json.dumps([0])
                        else:
                            row[idparent] = 0
                else:
                    if is_array:
                        row[idparent] = json.dumps(row[idparent])
                    else:
                        row[idparent] = row[idparent]

        # informacion para generar la vista del detalle
        data = {
            'breadcrumb': cls.breadcrumb,
            'campos': configuracion['campos'],
            'row': row,
            'id': id if id != 0 else '',
            'current_url': functions.generar_url(url_final),
            'save_url': functions.generar_url(url_save),
            'list_url': functions.generar_url(url_list),
        }

        ret = detalle.normal(data)
        return ret
