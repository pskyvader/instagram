from app.models.productocategoria import productocategoria as productocategoria_model

from .base import base
from .product_list import product_list


from .head import head
from .header import header
from .banner import banner
from .breadcrumb import breadcrumb
from .footer import footer

from core.app import app
from core.functions import functions


class product(base):
    def __init__(self):
        super().__init__(app.idseo,False)

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


        data = {}
        pl = product_list()  # product_list.php
        data["product_list"] = pl.product_list()  # Lista de productos, renderiza vista
        data["sidebar"] = pl.sidebar()  # genera sidebar, renderiza vista
        data.update(pl.orden_producto())  # genera lista de filtros
        data.update(pl.limit_producto())  # genera lista de cantidad de productos por pagina
        data.update(pl.pagination())  # genera paginador
        data.update(pl.is_search())  # Genera texto de busqueda, si existe

        ret["body"].append(("product/category", data))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

    def category(self, var=[]):
        ret = {"body": []}
        if len(var) > 0:
            id = functions.get_idseccion(var[0])
            categoria = productocategoria_model.getById(id)
            if len(categoria) > 0:
                self.url = functions.url_seccion(
                    [self.url[0], "category"], categoria, True
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
        ret["body"] += ba.individual(
            self.seo["banner"], self.seo["titulo"], self.metadata["title"]
        )["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        data = {}
        pl = product_list()  # product_list.py
        prod_list = pl.product_list(categoria)  # Lista de productos, renderiza vista
        sidebar = pl.sidebar(categoria)  # genera sidebar, renderiza vista
        data.update(pl.orden_producto())  # genera lista de filtros
        data.update(pl.limit_producto())  # genera lista de cantidad de productos por pagina
        data.update(pl.pagination())  # genera paginador
        data.update(pl.is_search())  # Genera texto de busqueda, si existe

        data["product_list"] = prod_list
        data["sidebar"] = sidebar

        ret["body"].append(("product/category", data))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

    def detail(self, var=[]):
        ret = {"body": []}
        if len(var) > 0:
            id = functions.get_idseccion(var[0])
            producto = producto_model.getById(id)
            if len(producto) > 0:
                self.url = functions.url_seccion(
                    [self.url[0], "detail"], producto, True
                )
                self.breadcrumb.append(
                    {
                        "url": functions.generar_url(self.url),
                        "title": producto["titulo"],
                    }
                )

        url_return = functions.url_redirect(self.url)
        if url_return != "":
            ret["error"] = 301
            ret["redirect"] = url_return
            return ret
        self.meta(producto)

        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        he = header()
        ret["body"] += he.normal()["body"]

        ba = banner()
        ret["body"] += ba.individual(
            self.seo["banner"], self.seo["titulo"], self.metadata["title"]
        )["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        pl = product_list()  # product_list.php
        sidebar = pl.sidebar()  # genera sidebar, renderiza vista
        pd = product_detail(producto, self.url)
        tabs = pd.tabs()
        pd.galeria()
        pd.resumen()

        data = {}
        data["tabs"] = tabs
        data["sidebar"] = sidebar
        data["url"] = functions.generar_url(self.url)

        if self.metadata["image"] != "":
            data["imagen_portada"] = self.metadata["image"]
        else:
            data["imagen_portada"] = self.metadata["logo"]

        ret["body"].append(("product/detail", data))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

