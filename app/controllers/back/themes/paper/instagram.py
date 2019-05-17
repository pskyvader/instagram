from .base import base

# from app.models.table import table as table_model
from app.models.administrador import administrador as administrador_model

# from app.models.modulo import modulo as modulo_model
# from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model
from app.models.configuracion import configuracion as configuracion_model

from app.models.igusuario import igusuario as igusuario_model
from app.models.igaccounts import igaccounts as igaccounts_model

# from .detalle import detalle as detalle_class
# from .lista import lista as lista_class
from .head import head
from .header import header
from .aside import aside
from .footer import footer

from core.app import app

# from core.database import database
from core.functions import functions

# from core.image import image
from core.socket import socket

import json


from instabot import Bot

from .instagram_bot import instagram_bot


class instagram(base):
    url = ["instagram"]
    metadata = {"title": "instagram", "modulo": "instagram"}
    breadcrumb = []
    bot = None

    @classmethod
    def index(cls):
        """Controlador de lista_class de elementos base, puede ser sobreescrito en el controlador de cada modulo"""
        ret = {"body": []}
        # Clase para enviar a controlador de lista_class
        class_name = cls.class_name
        url_final = cls.url.copy()

        if not administrador_model.verificar_sesion():
            url_final = ["login", "index"] + url_final
        # verificar sesion o redireccionar a login
        url_return = functions.url_redirect(url_final)
        if url_return != "":
            ret["error"] = 301
            ret["redirect"] = url_return
            return ret

        h = head(cls.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        he = header()
        ret["body"] += he.normal()["body"]

        asi = aside()
        ret["body"] += asi.normal()["body"]

        log = []
        total = 0
        mensaje_error = ""
        data = {}
        data["title"] = cls.metadata["title"]
        cls.breadcrumb = [
            {
                "url": functions.generar_url(url_final),
                "title": cls.metadata["title"],
                "active": "active",
            }
        ]
        data["breadcrumb"] = cls.breadcrumb
        data["log"] = log
        data["progreso"] = total
        data["mensaje_error"] = mensaje_error
        ret["body"].append(("instagram", data))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

    def update(self):
        ig=instagram_bot()
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = ig.update()
        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        socket.close()
        return ret


    def delete(self):
        ig=instagram_bot()
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta={'exito':False,'mensaje':''}
        users=igaccounts_model.getAll({'follower':False,'following':False,'favorito':False})
    
        ig=instagram_bot()
        bot=ig.bot
        for u in users:
            bot.unfollowed_file.append(u['pk'])
            igaccounts_model.delete(u[0])
        
        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        socket.close()
        return ret

    def user(self):
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {"exito": False, "mensaje": ""}
        if 'campos' in app.post and 'id' in app.post['campos']:
            campos = app.post["campos"]
            id = campos["id"]
            ig=instagram_bot()
            bot=ig.bot
            if id.isdigit():
                user=bot.get_user_info(id)
            else:
                user_id=bot.get_user_id_from_username(id)
                user=bot.get_user_info(user_id)
                
            if 'pk' not in user:
                respuesta['mensaje']="No se encontro un usuario valido"
            else:
                respuesta['exito']=True
                respuesta['mensaje']="Usuario: "+user['full_name']
        else:
            respuesta['mensaje']="No se encontraron datos validos"

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        socket.close()
        return ret


    def follow(self):
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {"exito": False, "mensaje": ""}
        if 'campos' in app.post and 'id' in app.post['campos']:
            campos = app.post["campos"]
            accion = campos["id"]
            ig=instagram_bot()
            respuesta = ig.follow(accion)
        else:
            respuesta['mensaje']="No se encontraron datos validos"

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        socket.close()
        return ret


    def unfollow(self):
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {"exito": False, "mensaje": ""}
        if 'campos' in app.post and 'id' in app.post['campos']:
            campos = app.post["campos"]
            accion = campos["id"]
            ig=instagram_bot()
            respuesta = ig.unfollow(accion)
        else:
            respuesta['mensaje']="No se encontraron datos validos"

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        socket.close()
        return ret
    
    def complete_process(self,var=[]):
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {"exito": False, "mensaje": ""}
        ig=instagram_bot()
        ig.bot.console_print("Actualizando usuarios")
        respuesta = ig.update()
        if not respuesta['exito']:
            ig.bot.console_print("Hubo un error al actualizar usuarios. Reiniciando bot para el siguiente paso")
            ig=instagram_bot()

        ig.bot.console_print("Dejando de seguir no seguidores")
        respuesta = ig.unfollow('nonfollower')
        
        if not respuesta['exito']:
            ig.bot.console_print("Hubo un error al dejar de seguir. Reiniciando bot para el siguiente paso")
            ig=instagram_bot()

        ig.bot.console_print("Siguiendo por hashtag")
        respuesta = ig.follow('hashtag')
        ig.bot.console_print("Todos los pasos completados")
        if len(var)==0:
            ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        socket.close()
        

        return ret