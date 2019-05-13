from core.app import app
from core.file import file
from core.functions import functions
from core.image import image
from core.view import view
from .head import head
from .header import header
from .aside import aside
from .footer import footer


from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model
from app.models.modulo import modulo as modulo_model


class detalle:
    metadata = {'title': ''}
    max_upload = "Ilimitado"

    def __init__(self, metadata):
        for key, value in metadata.items():
            self.metadata[key] = value

    def normal(self, data: dict):
        ret = {'body': []}
        campos = data['campos']
        row_data = data['row']
        row = []
        for k, v in campos.items():
            content = self.field(v, row_data)
            row.append( {'content': content, 'content_field': v['field'], 'class': 'hidden' if 'hidden' == v['type'] else ''})

        data['row'] = row
        data['title'] = self.metadata['title']

        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head['headers'] != '':
            return ret_head
        ret['body'] += ret_head['body']

        he = header()
        ret['body'] += he.normal()['body']

        asi = aside()
        ret['body'] += asi.normal()['body']

        ret['body'].append(('detail', data))

        f = footer()
        ret['body'] += f.normal()['body']
        return ret

    @staticmethod
    def configuracion(modulo: str, force=False):
        tipo_admin = str(app.session["tipo" + app.prefix_site])
        moduloconfiguracion = moduloconfiguracion_model.getByModulo(modulo)
        var = {'idmoduloconfiguracion': moduloconfiguracion[0]}
        if 'tipo' in app.get:
            var['tipo'] = app.get['tipo']
        modulo = modulo_model.getAll(var, {'limit': 1})
        modulo = modulo[0]
        estados = modulo['estado'][0]['estado']
        if 'true' != estados[tipo_admin] and not force:
            return {'error': 301, 'redirect': functions.url_redirect(['home'])}

        campos = {}
        for m in modulo['detalle']:
            if 'true' == m['estado'][tipo_admin]:
                campos[m['field']] = {'title_field': m['titulo'], 'field': m['field'], 'type': m['tipo'], 'required': 'true' == m['required'], 'help': m['texto_ayuda']}

        return {'campos': campos}

    def field(self, campos: dict, fila: dict, parent='', idparent=0, level=0):
        editor_count = 0
        if campos['type'] == 'active':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'active': fila[campos['field']] if campos['field'] in fila else '',
                'class': ('btn-success' if fila[campos['field']] else 'btn-danger') if campos['field'] in fila else 'btn-default',
                'icon': ('fa-check' if fila[campos['field']] else 'fa-close') if campos['field'] in fila else 'fa-question-circle',
            }
        elif campos['type'] == 'color':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'help': fila[campos['help']] if campos['help'] in fila else '',
                'value': fila[campos['field']] if campos['field'] in fila else '',
            }
        elif campos['type'] == 'date':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'help': fila[campos['help']] if campos['help'] in fila else '',
                'value': fila[campos['field']] if campos['field'] in fila else '',
            }
        elif campos['type'] == 'daterange':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'help': fila[campos['help']] if campos['help'] in fila else '',
                'value': fila[campos['field']] if campos['field'] in fila else '',
            }
        elif campos['type'] == 'editor':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'help': fila[campos['help']] if campos['help'] in fila else '',
                'value': fila[campos['field']] if campos['field'] in fila else '',
            }
            data['help'] += " (Tamaño máximo de archivo " + \
                self.max_upload + ")"
            if 0 == editor_count:
                theme = app.get_url() + 'static/' + 'assets/ckeditor/'
                t = '?t=I8BG'
                data['preload'] = [
                    {'url': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css', 'type': 'style'},
                    {'url': 'https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css', 'type': 'style'},
                    {'url': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js', 'type': 'script'},
                    {'url': 'https://code.jquery.com/jquery-1.11.3.min.js',
                        'type': 'script'},

                    {'url': theme + 'contents.css', 'type': 'style'},
                    {'url': theme + 'plugins/btgrid/styles/editor.css', 'type': 'style'},
                    {'url': theme + 'plugins/tableselection/styles/tableselection.css',
                        'type': 'style'},
                    {'url': theme + 'plugins/balloontoolbar/skins/default.css',
                        'type': 'style'},
                    {'url': theme + 'plugins/balloontoolbar/skins/moono-lisa/balloontoolbar.css', 'type': 'style'},
                    {'url': theme + 'plugins/balloonpanel/skins/moono-lisa/balloonpanel.css', 'type': 'style'},

                    {'url': theme + 'skins/moono-lisa/editor.css' + t, 'type': 'style'},
                    {'url': theme + 'plugins/basewidget/css/style.css' + t,
                        'type': 'style'},
                    {'url': theme + 'plugins/layoutmanager/css/style.css' + t,
                        'type': 'style'},
                ]

            else:
                data['preload'] = []

            editor_count += 1

        elif campos['type'] == 'grupo_pedido':
            direcciones = []
            if campos['field'] in fila:
                count = len(fila[campos['field']])
                for field in fila[campos['field']]:
                    field['title_field'] = campos['title_field']
                    field['field'] = campos['field']
                    direcciones.append(field.copy())

            else:
                count = 0

            for d in direcciones:
                d['lista_productos'] = campos['lista_productos']
                d['direccion_entrega'] = campos['direccion_entrega']
                for e in d['direccion_entrega']:
                    if e['idusuariodireccion'] == d['idusuariodireccion']:
                        e['selected'] = True
                    else:
                        e['selected'] = False

                for p in d['productos']:
                    p['lista_atributos'] = campos['lista_atributos']
                    for e in p['lista_atributos']:
                        if e['idproducto'] == p['idproductoatributo']:
                            e['selected'] = True
                        else:
                            e['selected'] = False

            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'help': campos['help'],
                'direcciones': direcciones,
                'direccion_entrega': campos['direccion_entrega'],
                'lista_productos': campos['lista_productos'],
                'lista_atributos': campos['lista_atributos'],
                'fecha': functions.current_time(),
                'count': str(count) if count > 0 else '',
            }

        elif campos['type'] == 'multiple':
            fields = []
            count = len(fila[campos['field']]) if campos['field'] in fila and isinstance(
                fila[campos['field']], list) else 0
            if count > 0:
                for key, f in enumerate(fila[campos['field']]):
                    td = []
                    for v in campos['columnas'].values():
                        content = self.field(v, f, campos['field'], key)
                        td.append(
                            {'content': content, 'content_field': v['field']})

                    linea = {'columna': td}
                    fields.append(linea)

                new_field = False
            else:
                new_field = True

            new_line = []
            # new fields, without values
            for v in campos['columnas'].values():
                content = self.field(v, {}, campos['field'])
                new_line.append(
                    {'content': content, 'content_field': v['field']})

            data = {
                'fields': fields,
                'count': count,
                'new_field': new_field,
                'new_line': new_line,
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
            }
        elif campos['type'] == 'multiple_text':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'parent': parent,
                'col': campos['col'],
                'required': campos['required'],
                'value': fila[campos['field']] if campos['field'] in fila else '',
            }
        elif campos['type'] == 'multiple_number':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'parent': parent,
                'col': campos['col'],
                'max': campos['max'],
                'required': campos['required'],
                'value': fila[campos['field']] if campos['field'] in fila else campos['default'],
            }
        elif campos['type'] == 'multiple_label':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'parent': parent,
                'col': campos['col'],
                'required': campos['required'],
                'value': fila[campos['field']] if campos['field'] in fila else '',
            }

        elif campos['type'] == 'multiple_hidden':
            data = {
                'field': campos['field'],
                'parent': parent,
                'required': campos['required'],
                'value': fila[campos['field']] if campos['field'] in fila else '',
            }
        elif campos['type'] == 'multiple_select':
            options = []
            for option in campos['option'].values():
                option['selected'] = (
                    campos['field'] in fila and fila[campos['field']] == option['value'])
                options.append(option.copy())

            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'parent': parent,
                'col': campos['col'],
                'option': options,
                'required': campos['required'],
            }
        elif campos['type'] == 'multiple_button':
            data = {
                'col': campos['col'],
            }
        elif campos['type'] == 'multiple_order':
            data = {
                'col': campos['col'],
            }
        elif campos['type'] == 'multiple_active':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'parent': parent,
                'col': campos['col'],
                'required': campos['required'],
                'active': str(fila[campos['field']]) if campos['field'] in fila else '',
                'class': ('btn-success' if fila[campos['field']] == 'true' else 'btn-danger') if campos['field'] in fila else 'btn-default',
                'icon': ('fa-check' if fila[campos['field']] == 'true' else 'fa-close') if campos['field'] in fila else 'fa-question-circle',
            }
        elif campos['type'] == 'multiple_active_array':
            array_campos = []
            for key in campos['array'].keys():
                key_copy = str(key)
                campos['array'][key]['active'] = str(
                    fila[campos['field']][key_copy]) if campos['field'] in fila and key_copy in fila[campos['field']] else 'true'
                campos['array'][key]['class'] = ('btn-success' if fila[campos['field']][key_copy] ==
                                                 'true' else 'btn-danger') if campos['field'] in fila and key_copy in fila[campos['field']] else 'btn-success'
                campos['array'][key]['icon'] = ('fa-check' if fila[campos['field']][key_copy] ==
                                                'true' else 'fa-close') if campos['field'] in fila and key_copy in fila[campos['field']] else 'fa-check'
                array_campos.append(campos['array'][key].copy())

            data = {
                'title_field': campos['title_field'],
                'array': array_campos,
                'field': campos['field'],
                'idparent': idparent,
                'parent': parent,
                'col': campos['col'],
                'required': campos['required'],
            }
        elif campos['type'] == 'image':
            image_url = image.generar_url( fila[campos['field']][0], 'thumb') if campos['field'] in fila and len(fila[campos['field']])>0 else ''
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'image': image_url,
                'is_image': '' != image_url,
                'url':  fila[campos['field']][0]['url'] if '' != image_url else '',
                'parent':  fila[campos['field']][0]['parent'] if '' != image_url else '',
                'folder':  fila[campos['field']][0]['folder'] if '' != image_url else '',
                'subfolder':  fila[campos['field']][0]['subfolder'] if '' != image_url else '',
                'help': campos['help'] if 'help' in campos else '',
            }
            data['help'] += " (Tamaño máximo de archivo " + \
                self.max_upload + ")"

        elif campos['type'] == 'multiple_image':
            fields = []
            if campos['field'] in fila:
                count = len(fila[campos['field']])
                for campo in fila[campos['field']]:
                    field = campo
                    field['title_field'] = campos['title_field']
                    field['field'] = campos['field']
                    field['image'] = image.generar_url(campo, 'thumb')
                    field['active'] = campo['portada']
                    field['class'] = 'btn-success' if 'true' == campo['portada'] else 'btn-danger'
                    field['icon'] = 'fa-check' if 'true' == campo['portada'] else 'fa-close'
                    fields.append(field.copy())
            else:
                count = 0

            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'help': campos['help'],
                'fields': fields,
                'count': count if count > 0 else ''
            }
        elif campos['type'] == 'file':
            file_url = file.generar_url(
                fila[campos['field']][0], '') if campos['field'] in fila and len(fila[campos['field']])>0 else ''
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'file': file_url,
                'is_file': '' != file_url,
                'url':  fila[campos['field']][0]['url'] if '' != file_url else '',
                'parent':  fila[campos['field']][0]['parent'] if '' != file_url else '',
                'folder':  fila[campos['field']][0]['folder'] if '' != file_url else '',
                'subfolder':  fila[campos['field']][0]['subfolder'] if '' != file_url else '',
                'help': campos['help'] if 'help' in campos else '',
            }
            data['help'] += " (Tamaño máximo de archivo " + \
                self.max_upload + ")"

        elif campos['type'] == 'multiple_file':
            fields = []
            if campos['field'] in fila:
                for campo in fila[campos['field']]:
                    field = campo
                    field['title_field'] = campos['title_field']
                    field['field'] = campos['field']
                    field['file'] = file.generar_url(campo, '')

                    fields.append(field.copy())

            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'help': campos['help'] if 'help' in campos else '',
                'fields': fields,
            }
            data['help'] += " (Tamaño máximo de archivo " + \
                self.max_upload + ")"

        elif campos['type'] == 'number':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'value': fila[campos['field']] if campos['field'] in fila else '',
                'help': campos['help'] if 'help' in campos else '',
            }
        elif campos['type'] == 'email':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'value': fila[campos['field']] if campos['field'] in fila else '',
            }
        elif campos['type'] == 'password':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
            }

        elif campos['type'] == 'token':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'value': fila[campos['field']] if campos['field'] in fila else '',
            }
        elif campos['type'] == 'map':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'direccion': fila[campos['field']]['direccion'] if campos['field'] in fila else '',
                'lat':  fila[campos['field']]['lat'] if campos['field'] in fila else '',
                'lng': fila[campos['field']]['lng'] if campos['field'] in fila else '',
            }

        elif campos['type'] == 'recursive_checkbox' or campos['type'] == 'recursive_radio':
            if 0 == level:
                if campos['field'] in fila:
                    count = len(fila[campos['field']])
                else:
                    if 'recursive_radio' == campos['type'] or campos['field'] in app.get:
                        count = 1
                    else:
                        count = 0
                data = {
                    'is_children': False,
                    'title_field': campos['title_field'],
                    'field': campos['field'],
                    'required': campos['required'],
                    'children': [],
                    'count': count if count > 0 else '',
                }
                for children in campos['parent'].values():
                    data['children'].append(self.field(campos.copy(), fila, '', children[0], 1))
            else:
                parent = campos['parent']
                checked = True if 0 == idparent else False
                if campos['field'] not in fila:
                    if campos['field'] in app.get:
                        checked = True if idparent == int(app.get[campos['field']]) else False
                else:
                    checked = True if str(idparent) in fila[campos['field']] else False
                data = {
                    'is_children': True,
                    'field': campos['field'],
                    'value': idparent,
                    'title': parent[idparent]['titulo'] if idparent in parent else '',
                    'checked': checked,
                    'required': campos['required'],
                    'level': (level - 1) * 20,
                    'children': [],
                }
                if idparent in parent:
                    campos['parent'] = parent[idparent]['children'].copy()

                    for children in campos['parent'].values():
                        data['children'].append(self.field(campos.copy(), fila, '', children[0], level + 1))

        elif campos['type'] == 'select':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'help': campos['help'] if 'help' in campos else '',
                'option': [],
            }
            for children in campos['parent']:
                selected = (0 == children[0])
                if campos['field'] not in fila:
                    if campos['field'] in app.get:
                        checked = (children[0] == app.get[campos['field']])

                else:
                    selected = (children[0] == fila[campos['field']])

                data['option'].append(
                    {'value': children[0], 'selected': selected, 'text': children['titulo']})

        elif campos['type'] == 'textarea':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'value': fila[campos['field']] if campos['field'] in fila else '',
            }
        elif campos['type'] == 'text':
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'value': fila[campos['field']] if campos['field'] in fila else '',
                'help': campos['help'] if 'help' in campos else '',
            }

        else:
            data = {
                'title_field': campos['title_field'],
                'field': campos['field'],
                'required': campos['required'],
                'value': fila[campos['field']] if campos['field'] in fila else '',
                'help': campos['help'] if 'help' in campos else '',
            }

        content = ('detail/'+campos['type'], data)
        return content

    @staticmethod
    def guardar(class_name):
        campos = app.post['campos']
        respuesta = {'exito': False, 'mensaje': ''}

        if campos['id'] == '':
            respuesta['id'] = class_name.insert(campos)
            respuesta['mensaje'] = "Creado correctamente"
        else:
            respuesta['id'] = campos['id']
            respuesta['id'] = class_name.update(campos)
            respuesta['mensaje'] = "Actualizado correctamente"

        respuesta['exito'] = True
        if isinstance(respuesta['id'], dict):
            return respuesta['id']
        return respuesta
