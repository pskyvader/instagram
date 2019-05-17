from .base_model import base_model
#from core.app import app
from core.database import database
#from .log import log
#from .productocategoria import productocategoria
#from .table import table
#import datetime
#import json

from .base_model import base_model


class igtotal(base_model):
    idname = 'idigtotal'
    table = 'igtotal'


    @classmethod
    def get_total(cls,tag,fecha,insert=False):
        from .table import table
        where = {'tag': tag,'fecha':fecha}
        connection = database.instance()
        row = connection.get(cls.table, cls.idname, where)
        if len(row) == 1:
            return row[0]
        else:
            data=where
            data['cantidad']=0
            if insert:
                cls.insert(data,False)
                return cls.get_total(tag,fecha)
            else:
                return data
    
    @classmethod
    def set_total(cls,tag,fecha,cantidad=1):
        if cantidad>0:
            row=cls.get_total(tag,fecha,True)
            data={}
            data['id']=row[0]
            data['cantidad']=row['cantidad']+cantidad
            return cls.update(data, False)
        else:
            return True