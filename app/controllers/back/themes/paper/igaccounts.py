from .base import base
from app.models.igaccounts import igaccounts as igaccounts_model

#from app.models.table import table as table_model
from app.models.administrador import administrador as administrador_model
#from app.models.modulo import modulo as modulo_model
#from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model

#from .detalle import detalle as detalle_class
from .lista import lista as lista_class
#from .head import head
#from .header import header
#from .aside import aside
#from .footer import footer
from .instagram_bot import instagram_bot

from core.app import app
#from core.database import database
from core.functions import functions
#from core.image import image

import json



class igaccounts(base):
    url = ['igaccounts']
    metadata = {'title' : 'igaccounts','modulo':'igaccounts'}
    breadcrumb = []
    def __init__(self):
        super().__init__(igaccounts_model)


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
            if int(get['tipo'])==1:
                where['following'] = True
            elif int(get['tipo'])==2:
                where['following'] = True
                where['follower'] = False
            elif int(get['tipo'])==3:
                where['following'] = True
                where['follower'] = True
            elif int(get['tipo'])==4:
                where['follower'] = True
            elif int(get['tipo'])==5:
                where['follower'] = True
                where['following'] = False
            elif int(get['tipo'])==6:
                where['follower'] = False
                where['following'] = False
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


        if 'update' in configuracion['th']:
            configuracion['th']['update']['action'] = configuracion['th']['update']['field']
            configuracion['th']['update']['field'] = 0
            configuracion['th']['update']['mensaje'] = 'Actualizando cuenta'

        if 'profile_url' in configuracion['th']:
            for v in respuesta['row']:
                v['profile_url'] = functions.ruta('https://www.instagram.com/'+v['username'])

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

    def update(self):
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        campos = app.post["campos"]
        respuesta = {"exito": False, "mensaje": ""}
        if 'id' in campos:
            id = int(campos["id"])
        else:
            id=None
            respuesta['mensaje']="No se encontró una ID valida"

        if id!=None:
            ig=instagram_bot()
            bot=ig.bot
            if bot!=None:
                user=igaccounts_model.getById(id)
                if 'pk' not in user:
                    id=None
                    respuesta['mensaje']="No se encontró un usuario valido"
            else:
                respuesta['mensaje']=ig.error_mensaje

        if id!=None and 'pk' in user:
            user=bot.get_user_info(user['pk'],False)
            if 'pk' in user:
                respuesta['exito']=True
                respuesta['mensaje']='Usuario actualizado correctamente'
            else:
                respuesta['mensaje']='No se encontró el usuario en Instagram. Intenta más tarde'

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret


    @classmethod
    def estado(cls):
        ret = {'headers': [ ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        campos = app.post['campos']
        respuesta = {'exito': False, 'mensaje': ''}
        set_query = {'id': campos['id'], campos['campo']: campos['active']}
        cls.class_name.update(set_query)
        respuesta['exito'] = True
        respuesta['mensaje'] = "Estado actualizado correctamente."

        if campos['campo']=='following':
            ig=instagram_bot()
            bot=ig.bot
            if bot!=None:
                user=igaccounts_model.getById(campos['id'])
                if 'pk' not in user:
                    respuesta['mensaje']="No se encontró un usuario valido"
                    respuesta['exito'] = False
            else:
                respuesta['mensaje']=ig.error_mensaje
                respuesta['exito'] = False

            if respuesta['exito']:
                if campos['active']=='true':
                    respuesta['exito'] = bot.follow(user['pk'],force=True)
                    if not respuesta['exito']:
                        respuesta['mensaje']='Error al seguir al usuario'
                else:
                    respuesta['exito'] = bot.unfollow(user['pk'])
                    if not respuesta['exito']:
                        respuesta['mensaje']='Error al dejar de seguir al usuario'

        ret['body'] = json.dumps( respuesta, ensure_ascii=False)
        return ret

    @classmethod
    def eliminar(cls):
        ret = {'headers': [
            ('Content-Type', 'application/json; charset=utf-8')], 'body': ''}
        campos = app.post['campos']
        respuesta = {'exito': False, 'mensaje': ''}
        user=igaccounts_model.getById(campos['id'])
        if user['favorito']:
            respuesta['mensaje']='No se puede eliminar, usuario en favoritos'
        else:
            ig=instagram_bot()
            bot=ig.bot
            if bot!=None:
                if 'pk' not in user:
                    respuesta['mensaje']="No se encontró un usuario valido"
                else:
                    if user['following']:
                        respuesta['exito'] = bot.unfollow(user['pk'])
                    else:
                        respuesta['exito'] = True
            else:
                respuesta['mensaje']=ig.error_mensaje


        if respuesta['exito']:
            cls.class_name.delete(campos['id'])
            respuesta['exito'] = True
            respuesta['mensaje'] = "Eliminado correctamente."


        ret['body'] = json.dumps(respuesta, ensure_ascii=False)
        return ret