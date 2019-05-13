from core.image import image
from core.functions import functions


class banner:
    sizes = [
        {"foto": "foto1", "size": "1200"},
        {"foto": "foto2", "size": "991"},
        {"foto": "foto3", "size": "768"},
        {"foto": "foto4", "size": "0"},
    ]

    def normal(self, row_banner=[]):
        ret = {"body": []}
        if len(row_banner) > 0:
            thumb = []
            banner = []
            for key, b in enumerate(row_banner):
                portada = image.portada(b["foto"])
                foto = image.generar_url(portada, "foto1")
                if foto != "":
                    thumb.append({"id": key, "active": (key == 0)})

                    srcset = self.srcset(portada)

                    banner.append(
                        {
                            "srcset": srcset,
                            "title": b["titulo"],
                            "active": (key == 0),
                            "data": "data-" if (key != 0) else "",
                            "foto": foto,
                            "texto1": b["texto1"],
                            "texto2": b["texto2"],
                            "link": functions.ruta(b["link"]),
                            "background": image.generar_url(portada, "color"),
                        }
                    )

            data = {}
            data["thumb"] = thumb
            data["banner"] = banner
            ret["body"].append(("banner", data))
        return ret

    def individual(self, foto_base, titulo, subtitulo=""):
        ret = {"body": []}
        foto_base = image.portada(foto_base)
        foto = image.generar_url(foto_base, "foto1")
        if foto != "":
            srcset = self.srcset(foto_base)
            banner = {
                "srcset": srcset,
                "title": functions.remove_tags(titulo),
                "subtitle": functions.remove_tags(subtitulo),
                "foto": foto,
                "background": image.generar_url(foto_base, "color"),
            }
        else:
            banner = {
                "title": functions.remove_tags(titulo),
                "subtitle": functions.remove_tags(subtitulo),
            }
        ret["body"].append(("banner-seccion", banner))
        return ret

    def srcset(self, foto_base):
        images = self.sizes
        srcset = []

        for size in images:
            foto = image.generar_url(foto_base, size["foto"], "webp")
            if foto != "":
                srcset.append(
                    {
                        "media": "(min-width: " + size["size"] + "px)",
                        "url": foto,
                        "type": "image/webp",
                    }
                )

        for size in images:
            foto = image.generar_url(foto_base, size["foto"])
            if foto != "":
                srcset.append(
                    {
                        "media": "(min-width: " + size["size"] + "px)",
                        "url": foto,
                        "type": "image/jpg",
                    }
                )

        return srcset
