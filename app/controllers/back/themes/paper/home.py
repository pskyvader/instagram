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
from app.models.configuracion import configuracion as configuracion_model

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
        # respuesta["total"] = igaccounts_model.getAll(select="total")
        where = {"follower": True}
        respuesta["follower"] = igaccounts_model.getAll(where, select="total")
        where = {"following": True}
        respuesta["following"] = igaccounts_model.getAll(where, select="total")
        where = {"follower": True, "following": True}
        respuesta["both"] = igaccounts_model.getAll(where, select="total")
        where = {"favorito": True}
        respuesta["favoritos"] = igaccounts_model.getAll(where, select="total")
        where = {"favorito": True, "follower": True}
        respuesta["favoritos-follower"] = igaccounts_model.getAll(where, select="total")
        where = {"favorito": True, "following": True}
        respuesta["favoritos-following"] = igaccounts_model.getAll(
            where, select="total"
        )
        where = {"favorito": True, "follower": True, "following": True}
        respuesta["favoritos-follower-following"] = igaccounts_model.getAll(
            where, select="total"
        )
        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    def get_hashtag_users(self, return_array=False):
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {}
        followers = {}
        following = {}
        removed = {}
        eficiencia = {}
        hashtag = ighashtag_model.getAll({"estado": True})
        hashtag2 = {
            h["hashtag"]: {"follower": 0, "following": 0, "removed": 0} for h in hashtag
        }

        f = igaccounts_model.getAll(
            {"follower": True, "hashtag!": ""},
            {"group": "hashtag"},
            "count(pk) as total,hashtag",
        )
        fl = igaccounts_model.getAll(
            {"following": True, "hashtag!": ""},
            {"group": "hashtag"},
            "count(pk) as total,hashtag",
        )
        r = igaccounts_model.getAll(
            {"following": False, "hashtag!": ""},
            {"group": "hashtag"},
            "count(pk) as total,hashtag",
        )

        for u in f:
            if u["hashtag"] in hashtag2:
                hashtag2[u["hashtag"]]["follower"] = u["total"]
        for u in fl:
            if u["hashtag"] in hashtag2:
                hashtag2[u["hashtag"]]["following"] = u["total"]
        for u in r:
            if u["hashtag"] in hashtag2:
                hashtag2[u["hashtag"]]["removed"] = u["total"]


        totales=[]
        for k, h in hashtag2.items():
            if return_array:
                nombre = k
            else:
                nombre = k.capitalize()
            f = h["follower"]
            fl = h["following"]
            r = h["removed"]
            porcentaje = (f / (fl + r)) * 100 if (fl + r > 0) else 0

            totales.append({'hashtag':nombre,'total':f+fl+r})
            porcentaje = round(porcentaje, 2)
            followers[nombre] = f
            following[nombre] = fl
            removed[nombre] = r
            eficiencia[nombre] = porcentaje


        respuesta["followers"] = {}
        respuesta["following"] = {}
        respuesta["removed"] = {}
        respuesta["eficiencia"] = {}
        totales = sorted(totales, key=lambda i: i["total"],reverse=True)
        for t in totales:
            respuesta["followers"][t['hashtag']] = followers[t['hashtag']]
            respuesta["following"][t['hashtag']] = following[t['hashtag']]
            respuesta["removed"][t['hashtag']] = removed[t['hashtag']]
            respuesta["eficiencia"][t['hashtag']] = eficiencia[t['hashtag']]

        if return_array:
            return respuesta
        else:
            ret["body"] = json.dumps(respuesta, ensure_ascii=False)
            return ret

    def get_total(self):
        from datetime import datetime, timedelta
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        
        days_seguidores_estadistica = int(
            configuracion_model.getByVariable("days_seguidores_estadistica", 30)
        )
        fecha_actual = datetime.now()
        fecha = (fecha_actual - timedelta(days=days_seguidores_estadistica)).strftime(
            "%Y-%m-%d"
        )
        respuesta = {
            "follows": {},
            "unfollows": {},
            "start_follow": {},
            "stop_follow": {},
        }
        
        totales = igtotal_model.getAll(where= {"DATE(fecha) >": fecha},condiciones={"order": "fecha ASC"})

        for t in totales:
            fecha = functions.formato_fecha(t["fecha"], "%d-%m-%Y")
            tag = t["tag"]
            cantidad = t["cantidad"]

            if (
                tag == "follows"
                or tag == "unfollows"
                or tag == "start_follow"
                or tag == "stop_follow"
            ):
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

    def get_total_followers(self):
        from datetime import datetime, timedelta

        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }

        days_seguidores_estadistica = int(
            configuracion_model.getByVariable("days_seguidores_estadistica", 30)
        )
        respuesta = {"follower": {}, "following": {}}

        fecha_actual = datetime.now()
        fecha_inicio = fecha_actual - timedelta(days=days_seguidores_estadistica)

        while fecha_inicio <= fecha_actual:
            fecha = fecha_inicio.strftime("%d-%m-%Y")
            respuesta["follower"][fecha] = 0
            respuesta["following"][fecha] = 0
            fecha_inicio += timedelta(days=1)

        fecha = (fecha_actual - timedelta(days=days_seguidores_estadistica)).strftime(
            "%Y-%m-%d"
        )
        follower = igaccounts_model.getAll(
            {"follower": True, "DATE(fecha) >": fecha},
            {"order": "fecha ASC", "group": 'DATE_FORMAT(fecha, "%d-%m-%Y")'},
            'count(pk) as total,DATE_FORMAT(fecha, "%d-%m-%Y") as fecha',
        )
        following = igaccounts_model.getAll(
            {"following": True, "DATE(fecha) >": fecha},
            {"order": "fecha ASC", "group": 'DATE_FORMAT(fecha, "%d-%m-%Y")'},
            'count(pk) as total,DATE_FORMAT(fecha, "%d-%m-%Y") as fecha',
        )

        for c in follower:
            respuesta["follower"][c["fecha"]] = c["total"]

        for c in following:
            respuesta["following"][c["fecha"]] = c["total"]

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret

