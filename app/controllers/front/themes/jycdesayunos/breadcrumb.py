from core.functions import functions
from app.models.seo import seo as seo_model


class breadcrumb:
    def normal(self, breadcrumb=[]):
        ret = {"body": []}
        seo = seo_model.getById(1)
        b = [{"url": functions.generar_url([seo["url"]]), "title": seo["titulo"]}]
        b = b + breadcrumb
        for bread in b:
            if b.index(bread) == len(b) - 1:
                bread["active"] = True
            else:
                bread["active"] = False

        data = {}
        data["breadcrumb"] = b.copy()
        last = b.pop()
        data["titulo"] = last["title"]

        if len(b) > 1:
            last = b.pop()
            data["subtitulo"] = last["title"]
        else:
            data["subtitulo"] = ""

        ret["body"].append(("breadcrumb", data))
        return ret
