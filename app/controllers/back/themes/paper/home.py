from core.app import app
from core.functions import functions
from .base import base
from .head import head
from .header import header
from .aside import aside
from .footer import footer
from app.models.administrador import administrador as administrador_model
from app.models.igaccounts import igaccounts as igaccounts_model
from app.models.ighashtag import ighashtag as ighashtag_model
from app.models.igtotal import igtotal as igtotal_model

import json


class home(base):
    url = ["home"]
    metadata = {"title": "Home", "modulo": "home"}

    @classmethod
    def index(cls):
        ret = {"body": []}
        url_final = cls.url.copy()
        if not administrador_model.verificar_sesion():
            url_final = ["login", "index", "home"]

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
        ret["body"].append(("home", data))

        f = footer()
        ret["body"] += f.normal()["body"]

        return ret

    def get_followers(self):
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {}
        # respuesta['total']=igaccounts_model.getAll(select='total')
        where = {"follower": True}
        respuesta["follower"] = igaccounts_model.getAll(where, select="total")
        where = {"following": True}
        respuesta["following"] = igaccounts_model.getAll(where, select="total")
        where = {"follower": True, "following": True}
        respuesta["both"] = igaccounts_model.getAll(where, select="total")
        where = {"favorito": True}
        respuesta["favoritos"] = igaccounts_model.getAll(where, select="total")
        # where={'favorito':True,'follower':True}
        # respuesta['favoritos-follower']=igaccounts_model.getAll(where,select='total')
        # where={'favorito':True,'following':True}
        # respuesta['favoritos-following']=igaccounts_model.getAll(where,select='total')
        # where={'favorito':True,'follower':True,'following':True}
        # respuesta['favoritos-follower-following']=igaccounts_model.getAll(where,select='total')
        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    def get_hashtag_users(self):
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {}
        # respuesta['total']=igaccounts_model.getAll(select='total')
        followers={}
        following={}
        removed={}
        hashtag = ighashtag_model.getAll({'estado':True})
        for h in hashtag:
            nombre=h["hashtag"].capitalize();
            f = igaccounts_model.getAll( {"hashtag": h["hashtag"],'follower':True}, select="total" )
            fl = igaccounts_model.getAll( {"hashtag": h["hashtag"],'following':True}, select="total" )
            r = igaccounts_model.getAll( {"hashtag": h["hashtag"],'following':False}, select="total" )
            porcentaje=int((f/(fl+r))*100);
            nombre+=' ('+str(porcentaje)+'%)'
            followers[nombre]=f
            following[nombre]=fl
            removed[nombre]=r

        respuesta['followers']=followers
        respuesta['following']=following
        respuesta['removed']=removed

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    def get_total(self):
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = { "follows": {}, "unfollows": {}, "start_follow": {}, "stop_follow": {}, }
        totales = igtotal_model.getAll(condiciones={"order": "fecha ASC"})

        for t in totales:
            fecha = functions.formato_fecha(t["fecha"],'%d-%m-%Y')
            tag = t["tag"]
            cantidad = t["cantidad"]

            if ( tag == "follows" or tag == "unfollows" or tag == "start_follow" or tag == "stop_follow" ):
                if fecha not in respuesta["follows"]:
                    respuesta["follows"][fecha] = 0

                if fecha not in respuesta["unfollows"]:
                    respuesta["unfollows"][fecha] = 0

                if fecha not in respuesta["start_follow"]:
                    respuesta["start_follow"][fecha] = 0

                if fecha not in respuesta["stop_follow"]:
                    respuesta["stop_follow"][fecha] = 0

                respuesta[tag][fecha] = cantidad

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret
