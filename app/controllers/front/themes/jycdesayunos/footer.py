from app.models.logo import logo as logo_model
from app.models.productocategoria import productocategoria as productocategoria_model
from app.models.seccion import seccion as seccion_model
from app.models.seo import seo as seo_model
from app.models.texto import texto as texto_model

from core.functions import functions
from core.image import image
from core.app import app
from core.view import view


class footer:
    def normal(self):
        ret = {"body": []}
        if "ajax" not in app.post:
            data = {}
            config = app.get_config()
            logo = logo_model.getById(6)
            portada = image.portada(logo["foto"])
            data["logo"] = image.generar_url(portada, "sitio")
            seo = seo_model.getById(1)
            data["path"] = functions.generar_url([seo["url"]], False)
            data["title"] = config["title"]

            informacion = []
            textos = texto_model.getAll({"tipo": 1})
            for t in textos:
                icono = ""
                link = ""
                if t[0] == 1:
                    icono = "fa-phone"
                    link = "tel:" + t["texto"]
                elif t[0] == 2:
                    icono = "fa-envelope-o"
                    link = "mailto:" + t["texto"]
                elif t[0] == 6:
                    icono = "fa-map-marker"
                informacion.append(
                    {
                        "icono": icono,
                        "title": t["titulo"],
                        "text": t["texto"],
                        "url": link,
                    }
                )

            data["informacion"] = informacion

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

            data["social"] = redes_sociales

            links_footer = []
            l = {"title": "Información", "links": [], "size": 3}
            row = seccion_model.getAll({"tipo": 3})
            seo = seo_model.getById(7)
            for seccion in row:
                l["links"].append(
                    {
                        "url": functions.url_seccion([seo["url"], "detail"], seccion),
                        "title": seccion["titulo"],
                    }
                )

            links_footer.append(l)

            l = {"title": "Productos", "links": [], "size": 3}
            row = productocategoria_model.getAll({"tipo": 1, "idpadre": 0})
            seo = seo_model.getById(8)
            for productos in row:
                l["links"].append(
                    {
                        "url": functions.url_seccion( [seo["url"], "category"], productos ),
                        "title": productos["titulo"],
                    }
                )

            links_footer.append(l)

            l = {"title": "Mi cuenta", "links": [], "size": 2}
            l["links"].append(
                {
                    "url": functions.generar_url(["cuenta", "datos"], False),
                    "title": "Mi cuenta",
                }
            )
            l["links"].append(
                {
                    "url": functions.generar_url(["cuenta", "direcciones"], False),
                    "title": "Mis direcciones",
                }
            )
            l["links"].append(
                {
                    "url": functions.generar_url(["cuenta", "pedidos"], False),
                    "title": "Mis pedidos",
                }
            )
            links_footer.append(l)

            data["links_footer"] = links_footer
            data["js"] = view.js()
            ret["body"].append(("footer", data))
        return ret
