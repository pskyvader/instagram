from core.image import image


class carousel:
    sizes = [
        {"foto": "foto1", "size": "1200"},
        {"foto": "foto2", "size": "991"},
        {"foto": "foto3", "size": "768"},
        {"foto": "foto4", "size": "0"},
    ]

    def normal(self, row_carousel=[], titulo=""):
        ret = {"body": []}
        if len(row_carousel) > 0:
            thumb = []

            for key, c in row_carousel:
                foto = image.generar_url(c, "thumb_carousel")

                if foto != "":
                    foto_w = image.generar_url(c, "thumb_carousel", "webp")
                    if foto_w != "":
                        srcset = [{"url": foto_w, "type": "image/webp"}]

                    thumb.append(
                        {
                            "srcset": srcset,
                            "id": key,
                            "title": titulo,
                            "active": (0 == key),
                            "foto": foto,
                        }
                    )

            carousel = []
            for key, c in row_carousel:
                foto = image.generar_url(c, "foto1")
                if foto != "":

                    srcset = self.srcset(c)

                    carousel.append(
                        {
                            "id": key,
                            "srcset": srcset,
                            "title": titulo,
                            "active": (0 == key),
                            "data": "data-" if (key != 0) else "",
                            "foto": foto,
                            "original": image.generar_url(c, ""),
                        }
                    )

            data = {}

            data["thumb"] = thumb
            data["carousel"] = carousel

            ret["body"].append(("carousel", data))
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
