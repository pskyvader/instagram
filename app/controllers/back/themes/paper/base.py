from core.app import app
from core.functions import functions
from core.image import image
from core.file import file
from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model
from app.models.modulo import modulo as modulo_model
from app.models.administrador import administrador as administrador_model
from app.models.table import table as table_model

from .lista import lista as lista_class
from .detalle import detalle as detalle_class

import importlib
import json


class base:
    url = []
    metadata = {'title': '', 'modulo': ''}
    class_name = None
    class_parent = None
    sub = None
    breadcrumb = []
    contiene_tipos = False
    contiene_hijos = False

    def init(self, var: list):
        from inspect import signature
        import inspect

        if len(var) == 0:
            var = ['index']

        if hasattr(self, var[0]) and callable(getattr(self, var[0])):
            fun = var[0]
            del var[0]
            method = getattr(self, fun)
            sig = signature(method)
            params = sig.parameters
            if 'self' in params:
                if 'var' in params:
                    ret = method(self, var=var)
                else:
                    ret = method(self)
            else:
                if 'var' in params:
                    ret = method(var=var)
                else:
                    ret = method()
        else:
            ret = {
                'error': 404
            }
        return ret

    @classmethod
    def __init__(cls, class_name=None):
        moduloconfiguracion = moduloconfiguracion_model.getByModulo(
            cls.metadata['modulo'])
        if 0 in moduloconfiguracion:
            cls.contiene_tipos = moduloconfiguracion['tipos'] if 'tipos' in moduloconfiguracion else False
            cls.sub = moduloconfiguracion['sub'] if 'sub' in moduloconfiguracion else ''
            cls.padre = moduloconfiguracion['padre'] if 'padre' in moduloconfiguracion else ''

            if cls.contiene_tipos and 'tipo' in app.get:
                tipo = app.get['tipo']
            else:
                tipo = 0

            modulo = modulo_model.getAll(
                {'idmoduloconfiguracion': moduloconfiguracion[0], 'tipo': tipo})

            if len(modulo) > 0:
                cls.contiene_hijos = modulo[0]['hijos'] if 'hijos' in modulo[0] else False
                cls.metadata['title'] = modulo[0]['titulo']

            if cls.padre != '':
                parent = 'app.models.' + cls.padre
                current_module = importlib.import_module(parent)
                cls.class_parent = getattr(current_module, cls.padre)

                if cls.class_parent.idname in app.get:
                    p = cls.class_parent.getById(
                        app.get[cls.class_parent.idname])
                    if len(p) > 0:
                        if 'titulo' in p and p['titulo'] != '':
                            cls.metadata['title'] += ' - '+p['titulo']
                        elif 'nombre' in p and p['nombre'] != '':
                            cls.metadata['title'] += ' - '+p['nombre']

        cls.class_name = class_name
        cls.breadcrumb = [
            {'url': functions.generar_url(
                ["home"]), 'title': 'Home', 'active': ''},
            {'url': functions.generar_url(cls.url), 'title': (
                cls.metadata['title']), 'active': 'active'}
        ]

    @classmethod
    def index(cls):
        '''Controlador de lista_class de elementos base, puede ser sobreescrito en el controlador de cada modulo'''
        ret = {'body': ''}
        # Clase para enviar a controlador de lista_class
        class_name = cls.class_name
        url_final = cls.url.copy()
        get = app.get
        if cls.contiene_tipos and not 'tipo' in get:
            url_final = ['home']
        if cls.contiene_hijos and not 'idpadre' in get:
            url_final = ['home']

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
        # controlador de lista_class
        lista = lista_class(cls.metadata)

        configuracion = lista.configuracion(cls.metadata['modulo'])
        if 'error' in configuracion:
            ret['error'] = configuracion['error']
            ret['redirect'] = configuracion['redirect']
            return ret
            
        head=lista.head()
        if head!=False:
            return head

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
        url_detalle = url_final.copy()
        url_detalle.append('detail')
        # obtener unicamente elementos de la pagina actual
        respuesta = lista.get_row(class_name, where, condiciones, url_detalle)

        if 'copy' in configuracion['th']:
            configuracion['th']['copy']['action'] = configuracion['th']['copy']['field']
            configuracion['th']['copy']['field'] = 0
            configuracion['th']['copy']['mensaje'] = 'Copiando'

        if cls.contiene_hijos:
            if cls.contiene_tipos:
                for v in respuesta['row']:
                    v['url_children'] = functions.generar_url(
                        url_final, {'idpadre': v[0], 'tipo': get['tipo']})

            else:
                for v in respuesta['row']:
                    v['url_children'] = functions.generar_url(
                        url_final, {'idpadre': v[0]})

        else:
            if 'url_children' in configuracion['th']:
                del configuracion['th']['url_children']

        if cls.sub != '':
            if cls.contiene_tipos:
                for v in respuesta['row']:
                    v['url_sub'] = functions.generar_url(
                        [cls.sub], {class_name.idname: v[0], 'tipo': get['tipo']})

            else:
                for v in respuesta['row']:
                    v['url_sub'] = functions.generar_url(
                        [cls.sub], {class_name.idname: v[0]})

        else:
            if 'url_sub' in configuracion['th']:
                del configuracion['th']['url_sub']

        # informacion para generar la vista de lista_class
        data = {
            'breadcrumb': cls.breadcrumb,
            'th': configuracion['th'],
            'current_url': functions.generar_url(url_final),
            'new_url': functions.generar_url(url_detalle),
        }

        data.update(respuesta)
        data.update(configuracion['menu'])
        ret = lista.normal(data)
        return ret

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
        detalle = detalle_class(metadata)
        configuracion = detalle.configuracion(metadata['modulo'])

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
            raiz = [{0: 0, 'titulo': 'Raíz', 'idpadre': [-1]}]
            categorias = raiz+categorias
            configuracion['campos']['idpadre']['parent'] = functions.crear_arbol( categorias, -1)
        elif cls.contiene_hijos or 'idpadre' in configuracion['campos']:
            configuracion['campos']['idpadre'] = {
                'title_field': 'idpadre', 'field': 'idpadre', 'type': 'hidden', 'required': True}
            if id == 0:
                if 'idpadre' in get:
                    row['idpadre'] = json.dumps([get['idpadre']])
                else:
                    row['idpadre'] = json.dumps([0])
            else:
                row['idpadre'] = json.dumps(row['idpadre'])
        else:
            if 'idpadre' in configuracion['campos']:
                del configuracion['campos']['idpadre']

        if cls.class_parent != None:
            class_parent = cls.class_parent
            idparent = class_parent.idname

            is_array = True
            fields = table_model.getByname(class_name.table)
            if idparent in fields and fields[idparent]['tipo'] != 'longtext':
                is_array = False

            if idparent in configuracion['campos']:
                categorias = class_parent.getAll()
                if is_array:
                    configuracion['campos'][idparent]['parent'] = functions.crear_arbol( categorias)
                else:
                    configuracion['campos'][idparent]['parent'] = categorias

            else:
                configuracion['campos'][idparent] = { 'title_field': idparent, 'field': idparent, 'type': 'hidden', 'required': True}
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

    @classmethod
    def orden(cls):
        respuesta = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        respuesta['body'] = json.dumps(
            lista_class.orden(cls.class_name), ensure_ascii=False)
        return respuesta

    @classmethod
    def estado(cls):
        respuesta = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        respuesta['body'] = json.dumps(
            lista_class.estado(cls.class_name), ensure_ascii=False)
        return respuesta

    @classmethod
    def eliminar(cls):
        respuesta = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        respuesta['body'] = json.dumps(
            lista_class.eliminar(cls.class_name), ensure_ascii=False)
        return respuesta

    @classmethod
    def copy(cls):
        respuesta = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        respuesta['body'] = json.dumps(
            lista_class.copy(cls.class_name), ensure_ascii=False)
        return respuesta

    @classmethod
    def excel(cls):
        get = app.get
        respuesta = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        respuesta['body'] = {'exito': False,
                             'mensaje': 'Debes recargar la pagina'}
        if cls.contiene_tipos and 'tipo' not in get:
            respuesta['body'] = json.dumps(
                respuesta['body'], ensure_ascii=False)
            return respuesta

        if cls.contiene_hijos and 'idpadre' not in get:
            respuesta['body'] = json.dumps(
                respuesta['body'], ensure_ascii=False)
            return respuesta

        where = {}
        if cls.contiene_tipos:
            where['tipo'] = get['tipo']

        if cls.contiene_hijos:
            where['idpadre'] = get['idpadre']

        if cls.class_parent != None:
            class_parent = cls.class_parent
            if class_parent.idname in get:
                where[class_parent.idname] = get[class_parent.idname]

        select = ""
        excel_data=lista_class.excel(cls.class_name, where, select, cls.metadata['title'])
        respuesta['body'] = json.dumps(excel_data, ensure_ascii=False)
        return respuesta

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

        respuesta['body'] = json.dumps(row, ensure_ascii=False)
        return respuesta

    @classmethod
    def regenerar(cls):
        respuesta = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        respuesta['body'] = json.dumps(
            image.regenerar(app.post), ensure_ascii=False)
        return respuesta

    @classmethod
    def guardar(cls):
        respuesta = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        respuesta['body'] = json.dumps(
            detalle_class.guardar(cls.class_name), ensure_ascii=False)
        return respuesta

    @classmethod
    def upload(cls):
        respuesta = {'headers': [ ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        respuesta['body'] = json.dumps( image.upload_tmp(cls.metadata['modulo']), ensure_ascii=False)
        return respuesta

    @classmethod
    def upload_file(cls):
        respuesta = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        respuesta['body'] = json.dumps(file.upload_tmp(), ensure_ascii=False)
        return respuesta
