from .base import base
from app.models.sitemap import sitemap as sitemap_model

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

from core.app import app
#from core.database import database
from core.cache import cache
from core.functions import functions
#from core.image import image


import json
from pathlib import Path
import os


class sitemap(base):
    url = ['sitemap']
    metadata = {'title': 'sitemap', 'modulo': 'sitemap'}
    breadcrumb = []

    def __init__(self):
        super().__init__(sitemap_model)

    @classmethod
    def index(cls):
        '''Controlador de lista_class de elementos base, puede ser sobreescrito en el controlador de cada modulo'''
        ret = {'body': []}
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

        h = head(cls.metadata)
        ret_head = h.normal()
        if ret_head['headers'] != '':
            return ret_head
        ret['body'] += ret_head['body']

        he = header()
        ret['body'] += he.normal()['body']

        asi = aside()
        ret['body'] += asi.normal()['body']

        row = class_name.getAll({'ready': True, 'valid': ''}, {
                                'order': 'idsitemap DESC'})
        log = []
        for r in row:
            log.append({'url': r['url']})
        listos = class_name.getAll({'ready': True}, select='total')
        pendientes = class_name.getAll({'ready': False}, select='total')
        if listos == 0 and pendientes == 0:
            total = 0
        else:
            total = (listos * 100) / (listos + pendientes)

        dir = app.get_dir(True)
        mensaje_error = ''
        my_file = Path(dir + 'sitemap.xml')
        if my_file.is_file():
            if not os.access(dir + 'sitemap.xml', os.W_OK):
                mensaje_error = 'Debes dar permisos de escritura o eliminar el archivo ' + \
                    dir + 'sitemap.xml'
        elif not os.access(dir, os.W_OK):
            mensaje_error = 'Debes dar permisos de escritura en ' + dir + \
                ' o crear el archivo sitemap.xml con permisos de escritura'

        data = {}
        data['title'] = cls.metadata['title']
        cls.breadcrumb = [{'url': functions.generar_url(
            url_final), 'title': cls.metadata['title'], 'active':'active'}]
        data['breadcrumb'] = cls.breadcrumb
        data['log'] = log
        data['progreso'] = total
        data['mensaje_error'] = mensaje_error
        data['url_sitemap'] = functions.generar_url(
            ['sitemap.xml'], front_auto=False)
        ret['body'].append(('sitemap', data))
        f = footer()
        ret['body'] += f.normal()['body']
        return ret

    def vaciar(self):
        ret = {'headers': [ ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        class_name = self.class_name
        respuesta = class_name.truncate()
        respuesta['vacio'] = True
        ret['body'] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    def generar(self):
        ret = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        class_name = self.class_name
        respuesta = {'exito': False, 'mensaje': ''}
        row = class_name.getAll()
        sitio_base = app.get_url(True)
        if len(row) == 0:
            r = self.head(sitio_base, sitio_base)
            valido = r['mensaje']
            ready = (valido != '')
            if 'new_url' in r and r['new_url'] != '':
                valido += " redirect " + r['new_url']
                ready = True

            insert = {'idpadre': 0, 'url': sitio_base,
                      'depth': 0, 'valid': valido, 'ready': ready}
            id = class_name.insert(insert)
            if not r['exito'] and 'new_url' in r and r['new_url'] != '':
                existe = class_name.getAll({'url': r['new_url']}, {'limit': 1})
                if len(existe) == 0:
                    insert = {
                        'idpadre': id, 'url': r['new_url'], 'depth': 1, 'valid': "", 'ready': False}
                    id = class_name.insert(insert)
            respuesta['exito'] = True
        else:
            row = class_name.getAll({'ready': False})
            if len(row) == 0:
                respuesta = self.generar_sitemap()
            else:
                sitio = row[0]
                depth = sitio['depth']
                url = sitio['url']
                if sitio['valid'] == '':
                    sub_sitios = self.generar_url(url, sitio_base)
                else:
                    sub_sitios = False

                if isinstance(sub_sitios, list):
                    update = {'id': sitio[0], 'idpadre': sitio['idpadre'], 'url': sitio['url'],
                              'depth': depth, 'valid': sitio['valid'], 'ready': True}
                    class_name.update(update)
                    id_padre = sitio[0]
                    depth += 1
                    for sitios in sub_sitios:
                        existe = class_name.getAll(
                            {'url': sitios}, {'limit': 1})
                        if len(existe) == 0:
                            r = self.head(sitios, sitio_base)
                            valido = r['mensaje']
                            ready = (valido != '')
                            if 'new_url' in r and r['new_url'] != '':
                                valido += " redirect " + r['new_url']
                                ready = True

                            insert = {'idpadre': id_padre, 'url': sitios,
                                      'depth': depth, 'valid': valido, 'ready': ready}
                            id = class_name.insert(insert)
                            if not r['exito'] and 'new_url' in r and r['new_url'] != '':
                                existe = class_name.getAll(
                                    {'url': r['new_url']}, {'limit': 1})
                                if len(existe) == 0:
                                    insert = {
                                        'idpadre': id, 'url': r['new_url'], 'depth': depth + 1, 'valid': "", 'ready': False}
                                    id = class_name.insert(insert)
                else:
                    update = {'id': sitio[0], 'idpadre': sitio['idpadre'], 'url': sitio['url'],
                              'depth': depth, 'valid': sitio['valid'], 'ready': True}
                    class_name.update(update)

                respuesta['exito'] = True

        listos = class_name.getAll({'ready': True}, select='total')
        row = class_name.getAll({'ready': True, 'valid': ''}, {
                                'limit': 1, 'order': 'idsitemap DESC'})
        if len(row) == 1:
            respuesta['ultimo'] = row[0]
        else:
            respuesta['ultimo'] = None

        pendientes = class_name.getAll({'ready': False}, select='total')
        if listos == 0 and pendientes == 0:
            total = 0
        else:
            total = (listos * 100) / (listos + pendientes)

        respuesta['progreso'] = total
        ret['body'] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    def generar_sitemap(self):
        class_name = self.class_name
        respuesta = {'exito': False, 'mensaje': '', 'generado': True}
        lista = class_name.getAll({'valid': ''}, {'order': 'depth'})

        body = '<?xml version="1.0" encoding="UTF-8"?>' + "\n"
        body += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "\n"

        count = -1
        total = len(lista)
        for value in lista:
            count += 1
            prioridad = (total - count) / total
            prioridad = prioridad if prioridad >= 0.1 else 0.1

            elemento = '<url>' + "\n"
            elemento += '<loc>' + value['url'] + '</loc>' + "\n"
            elemento += '<changefreq>monthly</changefreq>' + "\n"
            elemento += '<priority>' + \
                round(prioridad, 2) + '</priority>' + "\n"
            # elemento+='<lastmod>'+value['profundidad']+'</lastmod>' //<lastmod>2005-01-01</lastmod>
            elemento += '</url>' + "\n"
            body += elemento

        body += '</urlset>'
        dir = app.get_dir(True)

        try:
            file_write = open(dir + 'sitemap.xml', 'w+')
            file_write.write(body)
            file_write.close()
            respuesta['exito'] = True
        except:
            respuesta['exito'] = False
            respuesta['mensaje'] = 'Error al guardar el archivo en ' + \
                dir + 'sitemap.xml'
        cache.delete_cache()

        return respuesta

    def generar_url(self, sitio, sitio_base):
        from bs4 import BeautifulSoup
        import urllib.request

        sublista = []
        try:
            html_page = urllib.request.urlopen(sitio)
            soup = BeautifulSoup(html_page)
            for link in soup.findAll('a', href=True):
                url = link['href']
                if url.startswith(sitio_base):
                    sublista.append(sitio + url)

            return sublista
        except Exception as e:
            print('error:', e)
            return False

    def head(self, sitio, sitio_base, count=0):
        import urllib.request
        respuesta = {'exito': True, 'mensaje': self.validar_url(sitio, sitio_base)}
        if respuesta['mensaje'] == '':
            try:
                response = urllib.request.urlopen(sitio)
                response.getcode()
                if response.getcode() != 200:
                    if response.getcode() >= 300 and response.getcode() < 400:
                        if isinstance(response.headers['Location'], list):
                            response.headers['Location'] = response.headers['Location'][0]

                        location = self.head(
                            response.headers['Location'], sitio_base, count+1)
                        respuesta['new_url'] = location['new_url'] if 'new_url' in location else response.headers['Location']
                        if isinstance(respuesta['new_url'], list):
                            respuesta['new_url'] = respuesta['new_url'][0]
                        respuesta['mensaje'] = location['mensaje']
                        respuesta['exito'] = False
                    else:
                        respuesta['mensaje'] = 'status: ' + response.getcode()
            except Exception as e:
                respuesta['exito']=False
                respuesta['mensaje'] = 'error: ' + repr(e)
        return respuesta

    def validar_url(self, sitio, sitio_base):
        list_test = ['#', "../", 'javascript',
                     'whatsapp', 'facebook', 'mailto:', 'tel:']
        if any(s in sitio for s in list_test):
            return 'invalid'
        elif sitio.startswith(sitio_base):
            return ''
        else:
            return 'domain'
