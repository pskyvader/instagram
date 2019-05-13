from .base import base


from app.models.configuracion import configuracion as configuracion_model
from app.models.producto import producto as producto_model
from app.models.productocategoria import productocategoria as productocategoria_model

from core.app import app
from core.functions import functions
from core.image import image


class product_list(base):
    view = "grid"
    order = "orden"
    search = ""
    page = 1
    limit = 6
    count = 0

    def __init__(self):
        super().__init__(app.idseo,False)

        self.view = (
            "list" if "view" in app.get and app.get["view"] == "list" else "grid"
        )
        self.order = (
            functions.remove_tags(app.get["order"]).strip()
            if "order" in app.get and app.get["order"] != ""
            else "orden"
        )
        self.search = (
            functions.remove_tags(app.get["search"]).strip()
            if "search" in app.get
            else ""
        )
        self.page = (
            int(functions.remove_tags(app.get["page"]).strip())
            if "page" in app.get and app.get["page"] != ""
            else 1
        )
        self.limit = (
            int(functions.remove_tags(app.get["limit"]).strip())
            if "limit" in app.get and app.get["limit"] != ""
            else 6
        )

    def is_search(self):
        return {"search": self.search}

    def sidebar(self, categoria=None):
        variables = {}
        if self.seo["tipo_modulo"] != 0:
            variables["tipo"] = self.seo["tipo_modulo"]

        if self.modulo["hijos"]:
            if categoria == None:
                variables["idpadre"] = 0
            else:
                variables["idpadre"] = categoria[0]

        row = productocategoria_model.getAll(variables)
        sidebar_categories = []
        for s in row:
            sidebar_categories.append(
                {
                    "title": s["titulo"],
                    "active": "",
                    "url": functions.url_seccion(
                        [self.url[0], "category"], s, False, None
                    ),
                }
            )

        is_sidebar_categories = len(sidebar_categories) > 0
        is_sidebar_prices = False
        if is_sidebar_categories or is_sidebar_prices:
            is_sidebar = True
        else:
            is_sidebar = False

        if is_sidebar:
            data = {}
            data["title"] = "Categorias"
            data["is_sidebar_category"] = is_sidebar_categories
            data["sidebar_categories"] = sidebar_categories
            data["is_sidebar_prices"] = is_sidebar_prices
            return ("product/sidebar", data)
        else:
            return ""

    def orden_producto(self):
        orden_producto = configuracion_model.getByVariable("orden_producto")
        if not isinstance(orden_producto, bool):
            orden_producto = orden_producto.split(",")
            for key,op in enumerate(orden_producto):
                op = op.split(":")
                for k,o in enumerate(op):
                    op[k] = o.strip()
                orden_producto[key]=op

        if not isinstance(orden_producto, list) or len(orden_producto) == 0:
            orden_producto = [
                ["orden", "Recomendados"],
                ["ventas", "Más vendidos"],
                ["precio ASC", "Precio de menor a mayor"],
                ["precio DESC", "Precio de mayor a menor"],
                ["titulo ASC", "A-Z"],
                ["titulo DESC", "Z-A"],
            ]
            orden_producto_guardar = {}

            for op in orden_producto:
                orden_producto_guardar.append(":".join(op))

            orden_producto_guardar = ",".join(orden_producto_guardar)
            configuracion_model.setByVariable("orden_producto", orden_producto_guardar)

        orden_producto_mostrar = []
        for op in orden_producto:
            orden_producto_mostrar.append(
                {
                    "title": op[1],
                    "action": op[0],
                    "active": "order" in app.get and app.get["order"] == op[0],
                }
            )

        return {"view": self.view, "orden_producto": orden_producto_mostrar}

    def limit_producto(self):
        limits = {
            6: {"action": 6, "title": 6, "active": False},
            12: {"action": 12, "title": 12, "active": False},
            30: {"action": 30, "title": 30, "active": False},
            120: {"action": 120, "title": 120, "active": False},
        }

        if self.limit in limits:
            limits[self.limit]["active"] = True
        return {"limit_producto": limits.values()}

    def product_list(self, categoria=None):
        where = {}
        if self.seo["tipo_modulo"] != 0:
            where["tipo"] = self.seo["tipo_modulo"]

        if categoria != None:
            where[productocategoria_model.idname] = categoria[0]

        condiciones = {"order": self.order}
        if self.search != "":
            condiciones["palabra"] = self.search

        self.count = producto_model.getAll(where, condiciones, "total")

        condiciones["limit"] = self.limit
        if self.page > 1:
            condiciones["limit"] = (self.page - 1) * self.limit
            condiciones["limit2"] = self.limit

        productos = producto_model.getAll(where, condiciones)
        product_list = ""
        if len(productos) > 0:
            lista_productos = self.lista_productos(productos, "detail", "foto2")
            data = {}
            data["lista_productos"] = lista_productos
            if ( self.view == "grid" ):  # Comprobar si existe o no sidebar, para agrandar o achicar el tamaño del producto
                variables = {}
                if self.seo["tipo_modulo"] != 0:
                    variables["tipo"] = self.seo["tipo_modulo"]
                if self.modulo["hijos"]:
                    if categoria == None:
                        variables["idpadre"] = 0
                    else:
                        variables["idpadre"] = categoria[0]

                count = productocategoria_model.getAll(variables, {}, "total")
                if count > 0:
                    data["col_lg"] = "col-lg-6"
                else:
                    data["col_lg"] = "col-lg-4"

                data["col_md"] = "col-md-12"
                product_list = ("product/grid", data)
            else:
                product_list = ("product/list", data)

        return product_list

    def pagination(self):
        pagination = []
        rango = 5
        minimo = 1
        maximo = (int)(self.count / self.limit)
        if maximo < (self.count / self.limit):
            maximo += 1

        total = maximo
        sw = False
        page = self.page
        while maximo - minimo + 1 > rango:
            if sw:
                if minimo != page and minimo + 1 != page:
                    minimo += 1

            else:
                if maximo != page and maximo - 1 != page:
                    maximo -= 1

            sw = not sw

        aux_page = app.get["page"] if "page" in app.get else ""

        app.get["page"] = page - 1
        pagination.append(
            {
                "class_page": "previous " + ("" if page > 1 else "disabled"),
                "url_page": functions.generar_url(self.url)
                if page > 1
                else functions.generar_url(self.url, False),
                "text_page": '<i class="fa fa-angle-left"> </i>',
            }
        )

        for i in range(minimo, maximo + 1):
            app.get["page"] = i
            pagination.append(
                {
                    "class_page": "active" if page == i else "",
                    "url_page": functions.generar_url(self.url),
                    "text_page": i,
                }
            )

        app.get["page"] = page + 1
        pagination.append(
            {
                "class_page": "next " + ("" if page < total else "disabled"),
                "url_page": functions.generar_url(self.url) if page < total else functions.generar_url(self.url, False),
                "text_page": '<i class="fa fa-angle-right"> </i> ',
            }
        )

        if aux_page != "":
            app.get["page"] = aux_page
        else:
            del app.get["page"]

        return {"pagination": pagination}

    def lista_productos(self, row, url="detail", recorte="foto1"):
        lista = []
        for v in row:
            portada = image.portada(v["foto"])
            c = {
                "id": v[0],
                "title": v["titulo"],
                "price": functions.formato_precio(v["precio_final"]),
                "old_price": functions.formato_precio(v["precio"]),
                "stock": v["stock"],
                "image": image.generar_url(portada, recorte),
                "description": functions.remove_tags(v["resumen"]),
                "srcset": [],
                "url": functions.url_seccion([self.url[0], url], v),
            }
            src = image.generar_url(portada, recorte, "webp")
            if src != "":
                c["srcset"].append({"media": "", "src": src, "type": "image/webp"})

            if c["image"] != "":
                lista.append(c)

        return lista

