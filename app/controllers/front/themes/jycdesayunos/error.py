from .base import base

from .head import head
from .header import header
from .footer import footer

from core.cache import cache
from core.functions import functions


class error(base):
    url = ["error"]
    metadata = {"title": "error", "modulo": "error"}
    breadcrumb = []

    def __init__(self):
        cache.set_cache(False)

    @classmethod
    def index(cls, var=[]):
        ret = {"body": []}
        cls.metadata["modulo"] = cls.__class__.__name__

        h = head(cls.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        he = header()
        ret["body"] += he.normal()["body"]

        data = {}
        if len(var) > 0:
            data["error"] = var[0]

        ret["body"].append(("404", data))

        f = footer()
        ret["body"] += f.normal()["body"]

        return ret
