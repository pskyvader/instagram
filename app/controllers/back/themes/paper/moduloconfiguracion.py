from .base import base
from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model

#from app.models.table import table as table_model
from app.models.administrador import administrador as administrador_model
#from app.models.modulo import modulo as modulo_model
#from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model

from .detalle import detalle as detalle_class
from .lista import lista as lista_class
#from .head import head
#from .header import header
#from .aside import aside
#from .footer import footer

#from core.app import app
#from core.database import database
from core.functions import functions
#from core.image import image


#import json

class moduloconfiguracion(base):
    url = ['moduloconfiguracion']
    metadata = {'title': 'Configuracion de modulos',
                'modulo': 'moduloconfiguracion'}
    breadcrumb = []
    tipos_mostrar = {
        'action': {'text': 'Accion', 'value': 'action'},
        'active': {'text': 'Active', 'value': 'active'},
        'color': {'text': 'Color', 'value': 'color'},
        'delete': {'text': 'Eliminar', 'value': 'delete'},
        'image': {'text': 'Imagen', 'value': 'image'},
        'link': {'text': 'Link', 'value': 'link'},
        'text': {'text': 'Texto', 'value': 'text'},
    }
    tipos_detalle = {
        'active': {'text': 'Active', 'value': 'active'},
        'file': {'text': 'Archivo', 'value': 'file'},
        'multiple_file': {'text': 'Archivo multiple', 'value': 'multiple_file'},
        'recursive_checkbox': {'text': 'Arbol de botones checkbox', 'value': 'recursive_checkbox'},
        'recursive_radio': {'text': 'Arbol de botones radio', 'value': 'recursive_radio'},
        'color': {'text': 'Color', 'value': 'color'},
        'password': {'text': 'Contraseña', 'value': 'password'},
        'editor': {'text': 'Editor', 'value': 'editor'},
        'email': {'text': 'Email', 'value': 'email'},
        'date': {'text': 'Fecha', 'value': 'date'},
        'grupo_pedido': {'text': 'Grupos de pedido', 'value': 'grupo_pedido'},
        'image': {'text': 'Imagen', 'value': 'image'},
        'multiple_image': {'text': 'Imagen multiple', 'value': 'multiple_image'},
        'map': {'text': 'Mapa', 'value': 'map'},
        'multiple': {'text': 'Multiple', 'value': 'multiple'},
        'number': {'text': 'Numero', 'value': 'number'},
        'daterange': {'text': 'Rango de fechas', 'value': 'daterange'},
        'select': {'text': 'Select', 'value': 'select'},
        'text': {'text': 'Texto', 'value': 'text'},
        'textarea': {'text': 'Texto largo', 'value': 'textarea'},
        'token': {'text': 'Token', 'value': 'token'},
        'url': {'text': 'URL', 'value': 'url'},
    }

    def __init__(self):
        super().__init__(moduloconfiguracion_model)

    @classmethod
    def index(cls):
        '''Controlador de lista_class de elementos base, puede ser sobreescrito en el controlador de cada modulo'''
        ret = {'body': ''}
        # Clase para enviar a controlador de lista_class
        class_name = cls.class_name
        url_final = cls.url.copy()

        if not administrador_model.verificar_sesion():
            url_final = ['login', 'index'] + url_final
        # verificar sesion o redireccionar a login
        url_return = functions.url_redirect(url_final)
        if url_return != '':
            ret['error'] = 301
            ret['redirect'] = url_return
            return ret

        # cabeceras y campos que se muestran en la lista_class:
        # titulo,campo de la tabla a usar, tipo (ver archivo lista_class.py funcion "field")
        th = {
            # 'id' : {'title_th' : 'ID', 'field' : 0, 'type' : 'text'},
            'orden': {'title_th': 'Orden', 'field': 'orden', 'type': 'text'},
            'module': {'title_th': 'Modulo', 'field': 'module', 'type': 'text'},
            'titulo': {'title_th': 'Titulo', 'field': 'titulo', 'type': 'text'},
            'estado': {'title_th': 'Estado', 'field': 'estado', 'type': 'active'},
            'aside': {'title_th': 'Aparece en aside', 'field': 'aside', 'type': 'active'},
            # 'tipos' : {'title_th' : 'Contiene tipos', 'field' : 'tipos', 'type' : 'active'},
            'copy': {'title_th': 'Copiar', 'field': 0, 'type': 'action', 'action': 'copy', 'mensaje': 'Copiando Elemento'},
            'editar': {'title_th': 'Editar', 'field': 'url_detalle', 'type': 'link'},
            'subseccion': {'title_th': 'Modulos', 'field': 'url_subseccion', 'type': 'link'},
            'delete': {'title_th': 'Eliminar', 'field': 'delete', 'type': 'delete'},
        }

        # controlador de lista_class
        lista = lista_class(cls.metadata)
        head=lista.head()
        if head!=False:
            return head

        where = {}
        condiciones = {}
        url_detalle = url_final.copy()
        url_detalle.append('detail')
        # obtener unicamente elementos de la pagina actual
        respuesta = lista.get_row(class_name, where, condiciones, url_detalle)

        for value in respuesta['row']:
            value['url_subseccion'] = functions.generar_url(
                ['modulo'], {class_name.idname: value[0]})

        menu = {'new': True, 'excel': False, 'regenerar': False}

        # informacion para generar la vista de lista_class
        data = {
            'breadcrumb': cls.breadcrumb,
            'th': th,
            'current_url': functions.generar_url(url_final),
            'new_url': functions.generar_url(url_detalle),
        }

        data.update(respuesta)
        data.update(menu)
        ret = lista.normal(data)
        return ret

    @classmethod
    def detail(cls, var=[]):
        '''Controlador de detalle de elementos base, puede ser sobreescrito en el controlador de cada modulo'''
        ret = {'body': ''}
        # Clase para enviar a controlador de detalle
        class_name = cls.class_name
        url_list = cls.url.copy()
        url_save = cls.url.copy()
        url_final = cls.url.copy()
        metadata = cls.metadata.copy()
        url_save.append('guardar')
        url_final.append('detail')
        if len(var) > 0:
            id = int(var[0])
            url_final.append(id)
            metadata['title'] = 'Editar ' + metadata['title']
        else:
            id = 0
            metadata['title'] = 'Nuevo ' + metadata['title']

        cls.breadcrumb.append({'url': functions.generar_url(
            url_final), 'title': metadata['title'], 'active': 'active'})

        if not administrador_model.verificar_sesion():
            url_final = ['login', 'index'] + url_final
        # verificar sesion o redireccionar a login
        url_return = functions.url_redirect(url_final)
        if url_return != '':
            ret['error'] = 301
            ret['redirect'] = url_return
            return ret

        # cabeceras y campos que se muestran en el detalle:
        # titulo,campo de la tabla a usar, tipo (ver archivo detalle.py funcion "field")

        columnas_mostrar = {
            'orden': {'title_field': 'Orden', 'field': 'orden', 'type': 'multiple_order', 'required': True, 'col': 1},
            'field': {'title_field': 'Campo', 'field': 'field', 'type': 'multiple_text', 'required': True, 'col': 2},
            'titulo': {'title_field': 'Titulo', 'field': 'titulo', 'type': 'multiple_text', 'required': True, 'col': 3},
            'tipo': {'title_field': 'Tipo', 'field': 'tipo', 'type': 'multiple_select', 'required': True, 'option': cls.tipos_mostrar, 'col': 3},
            'button': {'field': '', 'type': 'multiple_button', 'col': 3},
        }
        columnas_detalle = {
            'orden': {'title_field': 'Orden', 'field': 'orden', 'type': 'multiple_order', 'required': True, 'col': 1},
            'field': {'title_field': 'Campo', 'field': 'field', 'type': 'multiple_text', 'required': True, 'col': 2},
            'titulo': {'title_field': 'Titulo', 'field': 'titulo', 'type': 'multiple_text', 'required': True, 'col': 3},
            'tipo': {'title_field': 'Tipo', 'field': 'tipo', 'type': 'multiple_select', 'required': True, 'option': cls.tipos_detalle, 'col': 3},
            'button': {'field': '', 'type': 'multiple_button', 'col': 3},
        }
        campos = {
            'module': {'title_field': 'Modulo', 'field': 'module', 'type': 'url', 'required': True, 'help': 'Modulo asociado'},
            'titulo': {'title_field': 'Titulo', 'field': 'titulo', 'type': 'text', 'required': True},
            'icono': {'title_field': 'Icono', 'field': 'icono', 'type': 'icon', 'required': True, 'help': 'Icono para barra lateral'},
            'sub': {'title_field': 'Sub seccion', 'field': 'sub', 'type': 'url', 'required': False, 'help': 'Modulo de subseccion, si existe'},
            'padre': {'title_field': 'Modulo padre', 'field': 'padre', 'type': 'text', 'required': False, 'help': 'Nombre del modulo padre, si existe'},
            'mostrar': {'title_field': 'Mostrar', 'field': 'mostrar', 'type': 'multiple', 'required': True, 'columnas': columnas_mostrar},
            'detalle': {'title_field': 'Detalle', 'field': 'detalle', 'type': 'multiple', 'required': True, 'columnas': columnas_detalle},
            'orden': {'title_field': 'Orden', 'field': 'orden', 'type': 'number', 'required': True},
            'estado': {'title_field': 'Estado', 'field': 'estado', 'type': 'active', 'required': True},
            'aside': {'title_field': 'Aside', 'field': 'aside', 'type': 'active', 'required': True},
            'tipos': {'title_field': 'Contiene Tipos', 'field': 'tipos', 'type': 'active', 'required': True},
        }

        # controlador de detalle
        detalle = detalle_class(metadata)
        row = class_name.getById(id) if id != 0 else []

        # informacion para generar la vista del detalle
        data = {
            'breadcrumb': cls.breadcrumb,
            'campos': campos,
            'row': row,
            'id': id if id != 0 else '',
            'current_url': functions.generar_url(url_final),
            'save_url': functions.generar_url(url_save),
            'list_url': functions.generar_url(url_list),
        }

        ret = detalle.normal(data)
        return ret
