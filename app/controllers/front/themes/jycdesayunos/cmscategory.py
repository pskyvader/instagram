from app.models.seccion import seccion as seccion_model
from app.models.seccioncategoria import seccioncategoria as seccioncategoria_model
from core.app import app
from core.functions import functions

from .base import base

from .head import head
from .header import header
from .banner import banner
from .breadcrumb import breadcrumb
from .footer import footer
from .carousel import carousel


class cmscategory(base):
    def __init__(self):
        super().__init__(app.idseo)

    def index(self):
        ret = {"body": []}
        self.meta(self.seo)
        url_return = functions.url_redirect(self.url)
        if url_return != "":
            ret["error"] = 301
            ret["redirect"] = url_return
            return ret

        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        he = header()
        ret["body"] += he.normal()["body"]

        ba = banner()
        ret["body"] += ba.individual(self.seo["banner"], self.metadata["title"])["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        var = {}
        if self.seo["tipo_modulo"] != 0:
            var["tipo"] = self.seo["tipo_modulo"]

        if self.modulo["hijos"]:
            var["idpadre"] = 0

        row = seccioncategoria_model.getAll(var)
        categories = self.lista(row)
        data = {}
        data["list"] = categories
        ret["body"].append(("cms-sidebar", data))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

    def detail(self, var=[]):
        ret = {"body": []}
        if len(var) > 0:
            id = functions.get_idseccion(var[0])
            categoria = seccioncategoria_model.getById(id)
            if 0 in categoria:
                self.url = functions.url_seccion(
                    [self.url[0], "detail"], categoria, True
                )
                self.breadcrumb.append(
                    {
                        "url": functions.generar_url(self.url),
                        "title": categoria["titulo"],
                    }
                )

        url_return = functions.url_redirect(self.url)
        if url_return != "":
            ret["error"] = 301
            ret["redirect"] = url_return
            return ret

        self.meta(categoria)

        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        he = header()
        ret["body"] += he.normal()["body"]

        ba = banner()
        ret["body"] += ba.individual(self.seo["banner"], self.seo["titulo"])["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        data = {}
        data["title"] = categoria["titulo"]
        data["description"] = categoria["descripcion"]
        ret["body"].append(("title-text", data.copy()))

        var = {}
        if self.seo["tipo_modulo"] != 0:
            var["tipo"] = self.seo["tipo_modulo"]

        if self.modulo["hijos"]:
            var["idpadre"] = categoria[0]

        row = seccioncategoria_model.getAll(var)
        categories = self.lista(row)
        data = {}
        data["list"] = categories
        ret["body"].append(("grid-border-3", data.copy()))

        var = {}
        if self.seo["tipo_modulo"] != 0:
            var["tipo"] = self.seo["tipo_modulo"]

        if self.modulo["hijos"]:
            var[seccioncategoria_model.idname] = categoria[0]

        row = seccion_model.getAll(var)

        if len(row) > 0:
            ret["body"].append(("title", {"title": "Secciones"}))
            secciones = self.lista(row, "sub", "lista")
            ret["body"].append(("grid-3", {"list": secciones}))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

    def sub(self, var=[]):
        ret = {"body": []}
        if len(var) > 0:
            id = functions.get_idseccion(var[0])
            seccion = seccion_model.getById(id)
            if 0 in seccion:
                self.url = functions.url_seccion([self.url[0], "sub"], seccion, True)
                self.breadcrumb.append(
                    {"url": functions.generar_url(self.url), "title": seccion["titulo"]}
                )

        url_return = functions.url_redirect(self.url)
        if url_return != "":
            ret["error"] = 301
            ret["redirect"] = url_return
            return ret

        self.meta(seccion)

        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        he = header()
        ret["body"] += he.normal()["body"]

        ba = banner()
        ret["body"] += ba.individual(self.seo["banner"], self.seo["titulo"])["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        data = {}
        data["title"] = seccion["titulo"]
        data["description"] = seccion["descripcion"]
        ret["body"].append(("title-text", data))

        ret["body"].append(("title", {"title": "Galería"}))

        car = carousel()
        ret["body"] += car.normal(seccion["foto"], seccion["titulo"])["body"]

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret
