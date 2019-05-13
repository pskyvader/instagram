from .base import base

from app.models.banner import banner as banner_model
from app.models.logo import logo as logo_model
from app.models.seo import seo as seo_model

from .head import head
from .footer import footer

from core.app import app
from core.functions import functions
from core.image import image


class application(base):
    url = ["home"]
    metadata = {"title": "home", "modulo": "home"}
    breadcrumb = []

    @classmethod
    def index(cls):
        """Controlador de lista_class de elementos base, puede ser sobreescrito en el controlador de cada modulo"""
        ret = {"body": []}
        # Clase para enviar a controlador de lista_class
        cls.metadata["modulo"] = cls.__class__.__name__

        h = head(cls.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        config = app.get_config()
        logo = logo_model.getById(5)
        portada = image.portada(logo["foto"])
        data = {}
        data["color_primario"] = config["color_primario"]
        data["color_secundario"] = config["color_secundario"]
        data["logo"] = image.generar_url(portada, "icono600")

        seo = seo_model.getById(1)
        data["path"] = functions.generar_url([seo["url"]])

        row_banner = banner_model.getAll({"tipo": 1})
        ba = banner()
        imgs = []
        for b in row_banner:
            if len(b["foto"]) > 0:
                portada = image.portada(b["foto"])
                foto = image.generar_url(portada, "foto1")
            else:
                foto = ""

            if foto != "":
                srcset = ba.srcset(portada)
                imgs = imgs + srcset

        images = []
        for i in imgs:
            images.append({"src": i["url"]})

        data["images"] = images

        ret["body"].append(("application", data))

        f = footer()
        ret["body"] += f.normal()["body"]

        return ret
