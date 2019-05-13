from core.cache import cache
from core.functions import functions
from core.image import image

from app.models.seo import seo as seo_model
from app.models.modulo import modulo as modulo_model
from app.models.moduloconfiguracion import (
    moduloconfiguracion as moduloconfiguracion_model,
)


class base:
    url = []
    metadata = {"title": "", "keywords": "", "description": ""}
    breadcrumb = []
    modulo = {}
    seo = []

    def init(self, var: list):
        from inspect import signature
        import inspect

        if len(var) == 0:
            var = ["index"]

        if hasattr(self, var[0]) and callable(getattr(self, var[0])):
            fun = var[0]
            del var[0]
            method = getattr(self, fun)
            sig = signature(method)
            params = sig.parameters
            if "self" in params:
                if "var" in params:
                    ret = method(self, var=var)
                else:
                    ret = method(self)
            else:
                if "var" in params:
                    ret = method(var=var)
                else:
                    ret = method()
        else:
            ret = {"error": 404}
        return ret

    @classmethod
    def __init__(cls, idseo, set_cache=True):
        if not set_cache:
            cache.set_cache(False)

        cls.seo = seo_model.getById(idseo)
        cls.url = [cls.seo["url"]]
        cls.breadcrumb = [
            {"url": functions.generar_url([cls.seo["url"]]), "title": cls.seo["titulo"]}
        ]
        cls.metadata["image"] = image.generar_url(
            image.portada(cls.seo["foto"]), "social"
        )
        cls.metadata["modulo"] = cls.__class__.__name__
        moduloconfiguracion = moduloconfiguracion_model.getByModulo(
            cls.seo["modulo_back"]
        )
        if 0 in moduloconfiguracion:
            modulo_list = modulo_model.getAll(
                {
                    "idmoduloconfiguracion": moduloconfiguracion[0],
                    "tipo": cls.seo["tipo_modulo"],
                },
                {"limit": 1},
            )
            if len(modulo_list) > 0:
                cls.modulo = modulo_list[0]

    def meta(self, meta):
        self.metadata["title"] = (
            meta["titulo"]
            if "titulo" in meta and meta["titulo"] != ""
            else self.metadata["title"]
        )
        self.metadata["keywords"] = (
            meta["keywords"]
            if "keywords" in meta and meta["keywords"] != ""
            else self.metadata["keywords"]
        )
        self.metadata["description"] = (
            meta["resumen"]
            if "resumen" in meta and meta["resumen"] != ""
            else self.metadata["description"]
        )
        self.metadata["description"] = (
            meta["descripcion"]
            if "descripcion" in meta and meta["descripcion"] != ""
            else self.metadata["description"]
        )
        self.metadata["description"] = (
            meta["metadescripcion"]
            if "metadescripcion" in meta and meta["metadescripcion"] != ""
            else self.metadata["description"]
        )
        if "foto" in meta and meta["foto"] != "":
            social = image.generar_url(image.portada(meta["foto"]), "social")
            if social != "":
                self.metadata["image"] = social

    def lista(self, row, url="detail", recorte="foto1"):
        lista = []
        for v in row:
            portada = image.portada(v["foto"])
            c = {
                "title": v["titulo"],
                "image": image.generar_url(portada, recorte),
                "description": v["resumen"],
                "srcset": [],
                "url": functions.url_seccion([self.url[0], url], v),
            }
            src = image.generar_url(portada, recorte, "webp")
            if src != "":
                c["srcset"].append({"media": "", "src": src, "type": "image/webp"})

            lista.append(c)

        return lista
