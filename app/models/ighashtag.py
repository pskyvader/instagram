from .base_model import base_model
from core.app import app
from core.database import database

# from .log import log
# from .productocategoria import productocategoria
# from .table import table
# import datetime
import json

from .base_model import base_model


class ighashtag(base_model):
    idname = "idighashtag"
    table = "ighashtag"

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

            if "hashtag" in fields:
                condiciones["buscar"]["hashtag"] = condiciones["palabra"]

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
    def getByHashtag(cls, hashtag: str):
        from .table import table
        where = {'hashtag': hashtag}
        condiciones={'limit':1}
        connection = database.instance()
        row = connection.get(cls.table, cls.idname, where,condiciones)
        if len(row) == 1:
            if 'idpadre' in row[0]:
                if row[0]['idpadre'] != '':
                    row[0]['idpadre'] = json.loads(row[0]['idpadre'])
                else:
                    row[0]['idpadre'] = []
            if 'foto' in row[0]:
                if row[0]['foto'] != '':
                    row[0]['foto'] = json.loads(row[0]['foto'])
                else:
                    row[0]['foto'] = []
            if 'archivo' in row[0]:
                if row[0]['archivo'] != '':
                    row[0]['archivo'] = json.loads(row[0]['archivo'])
                else:
                    row[0]['archivo'] = []
        return row[0] if len(row) == 1 else row