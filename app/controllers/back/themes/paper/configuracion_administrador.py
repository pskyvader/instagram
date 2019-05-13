from .base import base

from app.models.table import table as table_model
from app.models.administrador import administrador as administrador_model
from app.models.configuracion import configuracion as configuracion_model
from app.models.logo import logo as logo_model
from app.models.modulo import modulo as modulo_model
from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model

#from .detalle import detalle as detalle_class
#from .lista import lista as lista_class
from .head import head
from .header import header
from .aside import aside
from .footer import footer

from core.app import app
from core.database import database
from core.cache import cache
from core.functions import functions
#from core.image import image

import json


class configuracion_administrador(base):
    url = ['configuracion_administrador']
    metadata = {'title': 'Configuracion de administrador',
                'modulo': 'configuracion_administrador'}
    breadcrumb = []

    def __init__(self):
        super().__init__(None)

    @classmethod
    def index(cls):
        '''Controlador de lista_class de elementos base, puede ser sobreescrito en el controlador de cada modulo'''
        ret = {'body': []}
        # Clase para enviar a controlador de lista_class
        url_final = cls.url.copy()
        if not administrador_model.verificar_sesion():
            url_final = ['login', 'index'] + url_final
        # verificar sesion o redireccionar a login
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

        vaciar = table_model.getAll({'truncate': True}, {}, 'tablename')
        data = {}
        data['vaciar'] = vaciar
        data['breadcrumb'] = cls.breadcrumb
        data['title'] = cls.metadata['title']
        data['save_url'] = functions.generar_url(cls.url + ['vaciar'])
        data['list_url'] = functions.generar_url(cls.url)

        ret['body'].append(('configuracion_administrador', data))

        f = footer()
        ret['body'] += f.normal()['body']

        return ret

    def vaciar(self):
        ret = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        post = app.post
        if 'campos' in post:
            campos = post['campos']
            respuesta = table_model.truncate(campos)
            cache.delete_cache()
        else:
            respuesta = {'exito': False,
                         'mensaje': 'Debe seleccionar una tabla para vaciar'}
        ret['body'] = json.dumps(respuesta,ensure_ascii=False)
        return ret

    def json(self, responder=True):
        respuesta = {'exito': True, 'mensaje': 'JSON generado correctamente'}
        ret = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}

        base_dir = app.get_dir(True) + 'app/config/'
        row = table_model.getAll()
        campos = []
        for tabla in row:
            a = {
                'tablename': tabla['tablename'],
                'idname': tabla['idname'],
                'fields': tabla['fields'],
                'truncate': tabla['truncate'],
            }
            campos.append(a)

        file_write = open(base_dir + 'bdd.json', 'w+')
        file_write.write(json.dumps(campos))
        file_write.close()

        row = moduloconfiguracion_model.getAll()
        campos = []
        fields = table_model.getByname('moduloconfiguracion')
        fields_hijo = table_model.getByname('modulo')
        for tabla in row:
            a = database.create_data(fields, tabla)
            row_hijo = modulo_model.getAll({'idmoduloconfiguracion': tabla[0]})
            h = []

            for hijos in row_hijo:
                h.append(database.create_data(fields_hijo, hijos))

            a['hijo'] = h
            campos.append(a)

        file_write = open(base_dir + 'moduloconfiguracion.json', 'w+')
        file_write.write(json.dumps(campos))
        file_write.close()

        row = configuracion_model.getAll()
        campos = []
        fields = table_model.getByname('configuracion')
        for tabla in row:
            a = database.create_data(fields, tabla)
            campos.append(a)

        file_write = open(base_dir + 'configuracion.json', 'w+')
        file_write.write(json.dumps(campos))
        file_write.close()

        if responder:
            ret['body'] = json.dumps(respuesta,ensure_ascii=False)
            return ret
        else:
            return respuesta

    def json_update(self, responder=True):
        respuesta = {'exito': True, 'mensaje': [
            'JSON actualizado correctamente']}
        ret = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}

        base_dir = app.get_dir(True) + 'app/config/'

        file_read = open(base_dir + 'bdd.json', 'r')
        campos = json.loads(file_read.read())
        file_read.close()

        for key, tabla in enumerate(campos):
            tablename = tabla['tablename']
            # primero es siempre la tabla "tablas", se crea inmediatamente para guardar las siguientes configuraciones
            if key == 0:
                existe = table_model.table_exists(tablename)
                if not existe:
                    fields = {'titulo': tabla['idname'],
                              'tipo': 'int(11)', 'primary': True}
                    fields.update(dict(tabla['fields']))
                    for k, value in fields.items():
                        if not 'primary' in value:
                            fields[k]['primary'] = False
                    connection = database.instance()
                    connection.create(tablename, fields)

            table = table_model.getAll({'tablename': tablename})

            tabla['fields'] = json.dumps(tabla['fields'])
            if len(table) == 1:
                tabla['id'] = table[0][0]
                table_model.update(tabla, False)
            else:
                table_model.insert(tabla, False)

        tablas = table_model.getAll()

        for tabla in tablas:
            mensajes = table_model.validate(tabla[0], False)
            if not mensajes['exito']:
                respuesta = mensajes
                break
            else:
                respuesta['mensaje'] = respuesta['mensaje'] + \
                    mensajes['mensaje']

        row = administrador_model.getAll({'email': 'admin@mysitio.cl'})
        if len(row) == 0:
            insert_admin = {
                'pass': 12345678,
                'pass_repetir': 12345678,
                'nombre': 'Admin',
                'email': 'admin@mysitio.cl',
                'tipo': 1,
                'estado': True,
            }
            administrador_model.insert(insert_admin)

        row = logo_model.getAll()
        if len(row) == 0:
            insert_logo = [
                {'titulo': 'favicon', 'orden': 1},
                {'titulo': 'Logo login', 'orden': 2},
                {'titulo': 'Logo panel grande', 'orden': 3},
                {'titulo': 'Logo panel pequeño', 'orden': 4},
                {'titulo': 'Logo Header sitio', 'orden': 5},
                {'titulo': 'Logo Footer sitio', 'orden': 6},
                {'titulo': 'Manifest', 'orden': 7},
                {'titulo': 'Email', 'orden': 8},
            ]
            for logos in insert_logo:
                logo_model.insert(logos)

        file_read = open(base_dir + 'moduloconfiguracion.json', 'r')
        campos = json.loads(file_read.read())
        file_read.close()

        for moduloconfiguracion in campos:
            row = moduloconfiguracion_model.getAll(
                {'module': moduloconfiguracion['module']}, {'limit': 1})
            hijo = moduloconfiguracion['hijo'].copy()
            del moduloconfiguracion['hijo']

            moduloconfiguracion['mostrar'] = json.dumps(
                moduloconfiguracion['mostrar'])
            moduloconfiguracion['detalle'] = json.dumps(
                moduloconfiguracion['detalle'])
            if len(row) == 1:
                moduloconfiguracion['id'] = row[0][0]
                moduloconfiguracion['estado'] = row[0]['estado']
                moduloconfiguracion_model.update(
                    moduloconfiguracion.copy(), False)
                for h in hijo:
                    h['idmoduloconfiguracion'] = moduloconfiguracion['id']
                    row2 = modulo_model.getAll(
                        {'idmoduloconfiguracion': h['idmoduloconfiguracion'], 'tipo': h['tipo']}, {'limit': 1})

                    h['menu'] = json.dumps(h['menu'])
                    h['mostrar'] = json.dumps(h['mostrar'])
                    h['detalle'] = json.dumps(h['detalle'])
                    h['recortes'] = json.dumps(h['recortes'])
                    h['estado'] = json.dumps(h['estado'])
                    if len(row2) == 1:
                        h['id'] = row2[0][0]
                        h['estado'] = row2[0]['estado']
                        modulo_model.update(h, False)
                    else:
                        modulo_model.insert(h, False)

            else:
                moduloconfiguracion['estado'] = False
                id = moduloconfiguracion_model.insert( moduloconfiguracion, False)
                for h in hijo.values():
                    h['idmoduloconfiguracion'] = id
                    h['menu'] = json.dumps(h['menu'])
                    h['mostrar'] = json.dumps(h['mostrar'])
                    h['detalle'] = json.dumps(h['detalle'])
                    h['recortes'] = json.dumps(h['recortes'])
                    h['estado'] = json.dumps(h['estado'])
                    modulo_model.insert(h, False)

        file_read = open(base_dir + 'configuracion.json', 'r')
        campos = json.loads(file_read.read())
        file_read.close()
        for configuracion in campos:
            row = configuracion_model.getByVariable(configuracion['variable'])
            configuracion_model.setByVariable(
                configuracion['variable'], configuracion['valor'])

        cache.delete_cache()
        if responder:
            ret['body'] = json.dumps(respuesta,ensure_ascii=False)
            return ret
        else:
            return responder
