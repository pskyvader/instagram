from app.models.seccion import seccion as seccion_model
from core.app import app
from core.file import file
from core.functions import functions

from .base import base

from .head import head
from .header import header
from .banner import banner
from .breadcrumb import breadcrumb
from .footer import footer


class cmssidebar(base):
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
        ret["body"] += ba.individual(
            self.seo["banner"], self.metadata["title"], self.seo["subtitulo"]
        )["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        var = {}
        if self.seo["tipo_modulo"] != 0:
            var["tipo"] = self.seo["tipo_modulo"]

        if self.modulo["hijos"]:
            var["idpadre"] = 0

        row = seccion_model.getAll(var)
        sidebar = []
        for s in row:
            sidebar.append(
                {
                    "title": s["titulo"],
                    "active": "",
                    "url": functions.url_seccion([self.url[0], "detail"], s),
                }
            )

        data = {}

        data["title_category"] = self.seo["titulo"]
        data["sidebar"] = sidebar

        data["description"] = ""
        ret["body"].append(("cms-sidebar", data))
        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

    def detail(self, var=[]):
        ret = {"body": []}
        if len(var) > 0:
            id = functions.get_idseccion(var[0])
            seccion = seccion_model.getById(id)
            if 0 in seccion:
                self.url = functions.url_seccion([self.url[0], "detail"], seccion, True)
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
        ret["body"] += ba.individual(self.seo["banner"], self.seo["subtitulo"])["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        var = {}
        if self.seo["tipo_modulo"] != 0:
            var["tipo"] = self.seo["tipo_modulo"]

        if self.modulo["hijos"]:
            var["idpadre"] = 0

        row = seccion_model.getAll(var)
        sidebar = []
        for s in row:
            sidebar.append(
                {
                    "title": s["titulo"],
                    "active": "",
                    "url": functions.url_seccion([self.url[0], "detail"], s),
                }
            )

        extra = ""
        if len(seccion["archivo"]) > 0:
            files = []
            for a in seccion["archivo"]:
                files.append(
                    {
                        "title": a["url"],
                        "size": functions.file_size(file.generar_dir(a, "")),
                        "url": file.generar_url(a, ""),
                    }
                )
            data = {}
            data["files"] = files
            data["title"] = "Archivos"
            extra = ("file", data.copy())

        data = {}
        data["sidebar"] = sidebar
        data["title_category"] = self.seo["titulo"]
        data["title"] = seccion["titulo"]
        data["description"] = seccion["descripcion"]
        data["extra"] = extra
        ret["body"].append(("cms-sidebar", data))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret
