from core.functions import functions
from core.app import app
from core.image import image

from app.models.logo import logo as logo_model
from app.models.modulo import modulo as modulo_model
from app.models.moduloconfiguracion import (
    moduloconfiguracion as moduloconfiguracion_model,
)
from app.models.seo import seo as seo_model
from app.models.texto import texto as texto_model

import importlib


class header:
    data = {"logo": ""}

    def normal(self):
        ret = {"body": []}
        if "ajax" not in app.post:
            self.data["cart"] = self.header_cart()
            self.data["menu"] = self.menu()
            config = app.get_config()
            logo = logo_model.getById(5)
            portada = image.portada(logo["foto"])
            self.data["logo"] = image.generar_url(portada, "sitio")
            seo = seo_model.getById(1)
            self.data["path"] = functions.generar_url([seo["url"]], False)
            self.data["title"] = config["title"]

            telefono = texto_model.getById(1)
            self.data["telefono"] = telefono["texto"]
            email = texto_model.getById(2)
            self.data["email"] = email["texto"]
            seo = seo_model.getById(8)
            self.data["product_url"] = functions.generar_url([seo["url"]], False)
            self.data["search"] = (
                functions.remove_tags(app.get["search"]) if "search" in app.get else ""
            )
            
            self.data["header_top"] = self.header_top()
            ret["body"].append(("header", self.data))
        return ret

    def header_top(self):
        redes_sociales = []
        rss = texto_model.getAll({"tipo": 2})
        for r in rss:
            redes_sociales.append(
                {
                    "url": functions.ruta(r["url"]),
                    "icon": r["texto"],
                    "title": r["titulo"],
                }
            )
        data = {}
        data["telefono"]=self.data["telefono"]
        data["email"]=self.data["email"]
        data["social"] = redes_sociales
        return ("header-top", data)

    def header_cart(self):
        return ("header-cart", {})

    def menu(self):
        lista_menu = []
        seo = seo_model.getAll()
        for s in seo:
            if s["submenu"] and s["modulo_back"] != "" and s["modulo_back"] != "none":
                if s["menu"]:
                    url = functions.generar_url([s["url"]], False)
                else:
                    url = ""

                menu = {"titulo": s["titulo"], "link": url, "active": s["url"]}
                moduloconfiguracion = moduloconfiguracion_model.getByModulo(
                    s["modulo_back"]
                )
                if len(moduloconfiguracion) > 0:
                    modulo = modulo_model.getAll(
                        {
                            "idmoduloconfiguracion": moduloconfiguracion[0],
                            "tipo": s["tipo_modulo"],
                        },
                        {"limit": 1},
                    )
                    if len(modulo) > 0:
                        parent = "app.models." + s["modulo_back"]
                        current_module = importlib.import_module(parent)
                        self_class = getattr(current_module, s["modulo_back"])

                        var = {}
                        if s["tipo_modulo"] != 0:
                            var["tipo"] = s["tipo_modulo"]
                        if "hijos" in modulo[0] and modulo[0]["hijos"]:
                            var["idpadre"] = 0

                        row = self_class.getAll(var)
                        hijos = []
                        for sub in row:
                            sub_url = "detail"
                            if "link_menu" in s and s["link_menu"] != "":
                                sub_url = s["link_menu"]
                            hijos.append(
                                {
                                    "titulo": sub["titulo"],
                                    "link": functions.url_seccion(
                                        [s["url"], sub_url], sub
                                    ),
                                    "active": sub["url"],
                                }
                            )
                        menu["hijo"] = hijos

                lista_menu.append(menu)

            else:
                if s["menu"]:
                    lista_menu.append(
                        {
                            "titulo": s["titulo"],
                            "link": functions.generar_url([s["url"]], False),
                            "active": s["url"],
                        }
                    )

        menu = self.generar_menu(lista_menu)
        return menu

    def generar_menu(self, lista_menu, nivel=0, simple=False):
        menu_final = []
        nivel_maximo_hijo = 2
        for key, menu in enumerate(lista_menu):
            data = {"hijos": ""}
            data["contiene_hijo"] = (
                nivel < nivel_maximo_hijo
                and not simple
                and 'hijo' in menu
                and len(menu["hijo"]) > 0
            )
            if data["contiene_hijo"]:
                data["hijos"] = self.generar_menu(menu["hijo"], nivel + 1, simple)
            data["target"] = (
                'target="' + menu["target"] + '" rel="noopener noreferrer"'
                if "target" in menu
                else ""
            )
            data["active"] = ( "active" if nivel == 0 and not simple and functions.active(menu["active"]) else "" )
            data["prefetch"] = nivel == 0 and not simple
            data["url"] = menu["link"]
            data["title"] = menu["titulo"]
            data["nivel"] = nivel
            data["key"] = key
            menu_final.append(("menu", data))
        return menu_final
