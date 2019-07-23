from .base import base
from .configuracion_administrador import configuracion_administrador

#from app.models.table import table as table_model
from app.models.administrador import administrador as administrador_model
from app.models.configuracion import configuracion as configuracion_model
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
from core.functions import functions
#from core.image import image

import json
import os
from pathlib import Path


class update(base):
    url = ['update']
    metadata = {'title': 'update', 'modulo': 'update'}
    breadcrumb = []
    url_update = "http://pythonupdate.mysitio.cl/"
    dir = ''
    dir_update = ''
    archivo_log = ''
    no_update = ['app\\config\\config.json', 'app/config/config.json']

    def __init__(self):
        update.dir = app.get_dir(True)
        update.dir_update = self.dir + 'update/'
        update.archivo_log = app.get_dir(True) + '/log.json'

    @classmethod
    def index(cls):
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

        data['title'] = cls.metadata['title']
        cls.breadcrumb = [{'url': functions.generar_url(
            url_final), 'title': cls.metadata['title'], 'active':'active'}]
        data['breadcrumb'] = cls.breadcrumb

        mensaje_error = ''
        my_file = Path(cls.dir_update)
        if my_file.is_dir():
            if not os.access(cls.dir_update, os.W_OK):
                mensaje_error = 'Debes dar permisos de escritura al directorio ' + cls.dir_update
        elif not os.access(cls.dir, os.W_OK):
            mensaje_error = 'Debes dar permisos de escritura en ' + cls.dir + \
                ' o crear el directorio update/ con permisos de escritura'
        else:
            os.makedirs(cls.dir_update)

        data['mensaje_error'] = mensaje_error
        data['progreso'] = 0
        ret['body'].append(('update', data))

        f = footer()
        ret['body'] += f.normal()['body']

        return ret

    def vaciar_log(self):
        ret = {'body': ''}
        my_file = Path(self.archivo_log)
        if my_file.is_file():
            os.remove(self.archivo_log)
        ret['body'] = "'True'"
        return ret

    def get_update(self):
        '''Obtener nuevas actualizaciones desde url_update'''
        import urllib.request
        from distutils.version import LooseVersion
        ret = {'headers': [
            ('Content-Type', 'application/json charset=utf-8')], 'body': ''}
        respuesta = {'exito': False}
        url = self.url_update
        file = urllib.request.urlopen(url).read()
        file = json.loads(file)
        version_mayor = {'version': '0.0.0'}

        for f in file:
            if LooseVersion(f['version']) > LooseVersion(version_mayor['version']):
                del f['archivo']
                version_mayor = f

        version = configuracion_model.getByVariable('version','0.0.1')
        if isinstance(version, bool) or LooseVersion(version_mayor['version']) > LooseVersion(version):
            respuesta['version'] = version_mayor
            respuesta['exito'] = True
        else:
            respuesta['mensaje'] = 'No hay nuevas actualizaciones'

        ret['body'] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    def get_file(self):
        ret = {'headers': [
            ('Content-Type', 'application/json charset=utf-8')], 'body': ''}
        respuesta = {'exito': False, 'mensaje': ''}
        file = 'v' + app.post['file'] + '.zip'
        url = self.url_update + file
        path = self.dir_update + file
        if os.access(self.dir_update, os.W_OK):
            exito = self.download(url, path)
            if not isinstance(exito, bool):
                respuesta['mensaje'] = exito
            else:
                respuesta['exito'] = exito
                respuesta['archivo'] = app.post['file']
        else:
            respuesta['mensaje'] = 'Debes dar permiso de escritura a ' + \
                self.dir_update
        ret['body'] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    def download(self, url, path):
        import urllib.request
        try:
            urllib.request.urlretrieve(url, path)
        except:
            return 'Error al obtener el archivo '+url+'. Intenta mas tarde'
        return True

    def update_file(self):
        from time import time
        import zipfile
        ret = {'headers': [
            ('Content-Type', 'application/json charset=utf-8')], 'body': ''}
        respuesta = {'exito': False, 'mensaje': '', 'errores': []}
        file = None
        tiempo = time()
        id = 'v' + app.post['file'] + '.zip'
        inicio = int(app.post['inicio']) - 1 if 'inicio' in app.post else 0
        for root, dirs, files in os.walk(self.dir_update):
            for fichero in files:
                if id in fichero:
                    file = fichero
                    break

        if file is not None:
            file = self.dir_update + '/' + file
            if zipfile.is_zipfile(file):
                zip = zipfile.ZipFile(file, 'r')
                file_list = zip.infolist()
                total = len(file_list)
                for i in range(inicio, total):
                    nombre = file_list[i].filename
                    if nombre not in self.no_update:
                        try:
                            zip.extract(file_list[i], self.dir)
                        except Exception as e:
                            print(e)
                            respuesta['errores'].append(nombre)

                    if i % 500 == 0:
                        log = {'mensaje': 'Actualizando ...' + nombre[-30:] + ' (' + str(
                            i + 1) + '/' + str(total) + ')', 'porcentaje': ((i + 1) / total) * 90}
                        file_write = open(self.archivo_log, 'w+')
                        file_write.write(json.dumps(log, ensure_ascii=False))
                        file_write.close()

                    if functions.current_time(as_string=False) - tiempo > 15:
                        respuesta['inicio'] = i
                        break

                zip.close()
                if len(respuesta['errores']) == 0:
                    respuesta['exito'] = True
                else:
                    respuesta['mensaje'] = [
                        'Se encontraron errores de extraccion:']
                    respuesta['mensaje'] += respuesta['errores']
            else:
                respuesta['mensaje'] = 'Error al abrir archivo, o archivo no valido'
        else:
            respuesta['mensaje'] = 'archivo no encontrado'

        if 'inicio' not in respuesta:
            c = configuracion_administrador()
            c.json_update(False)

            log = {'mensaje': 'Actualización finalizada', 'porcentaje': 100}
            file_write = open(self.archivo_log, 'w+')
            file_write.write(json.dumps(log, ensure_ascii=False))
            file_write.close()
        ret['body'] = json.dumps(respuesta, ensure_ascii=False)
        return ret
