from .base import base
from app.models.configuracion import configuracion as configuracion_model

#from app.models.table import table as table_model
#from app.models.administrador import administrador as administrador_model
#from app.models.modulo import modulo as modulo_model
#from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model

#from .detalle import detalle as detalle_class
#from .lista import lista as lista_class
#from .head import head
#from .header import header
#from .aside import aside
#from .footer import footer

#from core.app import app
#from core.database import database
#from core.functions import functions
#from core.image import image


#import json

class configuracion(base):
    url = ['configuracion']
    metadata = {'title': 'configuracion', 'modulo': 'configuracion'}
    breadcrumb = []

    def __init__(self):
        super().__init__(configuracion_model)
