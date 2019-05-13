from .base_model import base_model

from core.app import app
from core.functions import functions
from core.database import database

# from .log import log
# from .productocategoria import productocategoria
# from .table import table
# import datetime
import json

from .base_model import base_model


class igaccounts(base_model):
    idname = "idigaccounts"
    table = "igaccounts"

    @classmethod
    def getAll(cls, where={}, condiciones={}, select=""):
        from .table import table as table_model

        condiciones = condiciones.copy()
        where = where.copy()
        limit = None
        idpadre = None
        return_total = None
        connection = database.instance()
        fields = table_model.getByname(cls.table)
        if "estado" not in where and app.front and "estado" in fields:
            where["estado"] = True

        if "idpadre" in where:
            if "idpadre" in fields:
                idpadre = where["idpadre"]
                if "limit" in condiciones:
                    limit = condiciones["limit"]
                    limit2 = 0
                    del condiciones["limit"]

                if "limit2" in condiciones:
                    if limit == None:
                        limit = 0
                    limit2 = condiciones["limit2"]
                    del condiciones["limit2"]
            del where["idpadre"]

        if "order" not in condiciones and "orden" in fields:
            condiciones["order"] = "orden ASC"

        if "palabra" in condiciones:
            condiciones["buscar"] = {}
            if "username" in fields:
                condiciones["buscar"]["username"] = condiciones["palabra"]
            if "full_name" in fields:
                condiciones["buscar"]["full_name"] = condiciones["palabra"]
            if "biography" in fields:
                condiciones["buscar"]["biography"] = condiciones["palabra"]
            if "titulo" in fields:
                condiciones["buscar"]["titulo"] = condiciones["palabra"]
            if "keywords" in fields:
                condiciones["buscar"]["keywords"] = condiciones["palabra"]
            if "descripcion" in fields:
                condiciones["buscar"]["descripcion"] = condiciones["palabra"]
            if "metadescripcion" in fields:
                condiciones["buscar"]["metadescripcion"] = condiciones["palabra"]
            if "cookie_pedido" in fields:
                condiciones["buscar"]["cookie_pedido"] = condiciones["palabra"]
            if len(condiciones["buscar"]) == 0:
                del condiciones["buscar"]

        if select == "total":
            return_total = True
            if idpadre != None:
                select = ""
        row = connection.get(cls.table, cls.idname, where, condiciones, select)
        deleted = False
        row_copy = []
        for r in row:
            deleted = False
            if "idpadre" in r:
                if r["idpadre"] != "":
                    r["idpadre"] = json.loads(r["idpadre"])
                else:
                    r["idpadre"] = []
                if idpadre != None and str(idpadre) not in r["idpadre"]:
                    deleted = True

            if return_total == None:
                if not deleted and "foto" in r:
                    if r["foto"] != "":
                        r["foto"] = json.loads(r["foto"])
                    else:
                        r["foto"] = []
                if not deleted and "archivo" in r:
                    if r["archivo"] != "":
                        r["archivo"] = json.loads(r["archivo"])
                    else:
                        r["archivo"] = []

            if not deleted:
                row_copy.append(r)

        row = row_copy

        if limit != None:
            if limit2 == 0:
                row = row[0:limit]
            else:
                row = row[limit : limit2 + 1]

        if return_total != None:
            if idpadre != None:
                return len(row)
            else:
                return row[0]["total"]
        else:
            return row

    @classmethod
    def getById(cls, id: int):
        from .table import table

        where = {cls.idname: id}
        if app.front:
            fields = table.getByname(cls.table)
            if "estado" in fields:
                where["estado"] = True

        connection = database.instance()
        row = connection.get(cls.table, cls.idname, where)
        if len(row) == 1:
            if "idpadre" in row[0]:
                if row[0]["idpadre"] != "":
                    row[0]["idpadre"] = json.loads(row[0]["idpadre"])
                else:
                    row[0]["idpadre"] = []
            if "foto" in row[0]:
                if row[0]["foto"] != "":
                    row[0]["foto"] = json.loads(row[0]["foto"])
                else:
                    row[0]["foto"] = []
            if "archivo" in row[0]:
                if row[0]["archivo"] != "":
                    row[0]["archivo"] = json.loads(row[0]["archivo"])
                else:
                    row[0]["archivo"] = []
        return row[0] if len(row) == 1 else row

    @classmethod
    def getByPK(cls, pk):
        where = {"pk": str(pk)}
        condiciones = {"limit": 1}
        connection = database.instance()
        row = connection.get(cls.table, cls.idname, where, condiciones)
        if len(row) == 1:
            if "idpadre" in row[0]:
                if row[0]["idpadre"] != "":
                    row[0]["idpadre"] = json.loads(row[0]["idpadre"])
                else:
                    row[0]["idpadre"] = []
            if "foto" in row[0]:
                if row[0]["foto"] != "":
                    row[0]["foto"] = json.loads(row[0]["foto"])
                else:
                    row[0]["foto"] = []
            if "archivo" in row[0]:
                if row[0]["archivo"] != "":
                    row[0]["archivo"] = json.loads(row[0]["archivo"])
                else:
                    row[0]["archivo"] = []

        return row[0] if len(row) == 1 else row

    @classmethod
    def insert_user(cls, user_info):
        data = {}
        data["pk"] = str(user_info["pk"])
        data["username"] = user_info["username"]
        if str(user_info["username"]).endswith("\\"):
            data["username"] = str(user_info["username"]).replace("\\", "\\\\")
        data["full_name"] = user_info["full_name"]
        if str(user_info["full_name"]).endswith("\\"):
            data["full_name"] = str(user_info["full_name"]).replace("\\", "\\\\")

        if "hd_profile_pic_url_info" in user_info:
            data["profile_pic_url"] = user_info["profile_pic_url"]["url"]
        elif "hd_profile_pic_versions" in user_info:
            data["profile_pic_url"] = list(user_info["hd_profile_pic_versions"]).pop()[
                "url"
            ]
        else:
            data["profile_pic_url"] = user_info["profile_pic_url"]

        data["biography"] = user_info["biography"]
        if str(user_info["biography"]).endswith("\\"):
            data["biography"] = str(user_info["biography"]).replace("\\", "\\\\")
        data["follower_count"] = user_info["follower_count"]
        data["following_count"] = user_info["following_count"]
        data["has_anonymous_profile_picture"] = user_info[
            "has_anonymous_profile_picture"
        ]
        data["is_private"] = user_info["is_private"]
        data["is_business"] = user_info["is_business"]
        data["is_verified"] = user_info["is_verified"]
        data["media_count"] = user_info["media_count"]
        data["datos"] = json.dumps(user_info)
        data["fecha"] = functions.current_time()
        data["following"] = False
        data["follower"] = False
        data["favorito"] = False
        return cls.insert(data, False)

    @classmethod
    def update_user(cls, id, user_info):
        data = {}
        data["id"] = id
        data["pk"] = str(user_info["pk"])
        data["username"] = user_info["username"]
        if str(user_info["username"]).endswith("\\"):
            data["username"] = str(user_info["username"]).replace("\\", "\\\\")
        data["full_name"] = user_info["full_name"]
        if str(user_info["full_name"]).endswith("\\"):
            data["full_name"] = str(user_info["full_name"]).replace("\\", "\\\\")

        if "hd_profile_pic_url_info" in user_info:
            data["profile_pic_url"] = user_info["profile_pic_url"]["url"]
        elif "hd_profile_pic_versions" in user_info:
            data["profile_pic_url"] = list(user_info["hd_profile_pic_versions"]).pop()[
                "url"
            ]
        else:
            data["profile_pic_url"] = user_info["profile_pic_url"]

        data["biography"] = user_info["biography"]
        if str(user_info["biography"]).endswith("\\"):
            data["biography"] = str(user_info["biography"]).replace("\\", "\\\\")
        data["follower_count"] = user_info["follower_count"]
        data["following_count"] = user_info["following_count"]
        data["has_anonymous_profile_picture"] = user_info[
            "has_anonymous_profile_picture"
        ]
        data["is_private"] = user_info["is_private"]
        data["is_business"] = user_info["is_business"]
        data["is_verified"] = user_info["is_verified"]
        data["media_count"] = user_info["media_count"]
        data["datos"] = json.dumps(user_info)
        return cls.update(data, False)
