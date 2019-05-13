from core.app import app
from core.functions import functions
from core.image import image
from .head import head
from .header import header
from .aside import aside
from .footer import footer

from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model
from app.models.modulo import modulo as modulo_model


class lista:
    metadata = {'title': ''}

    def __init__(self, metadata: dict):
        for key, value in metadata.items():
            self.metadata[key] = value

    def head(self):
        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head['headers'] != '':
            return ret_head
        else:
            return False
            
    def normal(self, data: dict):
        ret = {'body': []}
        th = data['th']
        row_data = data['row']
        row = []
        even = False
        for fila in row_data:
            td = []
            for k, v in th.items():
                content = self.field(v, fila)
                td.append({'content': content, 'content_field': v['field']})

            linea = {'even': even, 'id': fila[0], 'td': td,
                     'order': fila['orden'] if 'orden' in fila else ''}
            row.append(linea)
            even = not even

        data['row'] = row
        data['title'] = self.metadata['title']
        data['order'] = 'orden' in th

        data = self.pagination(data)

        data['delete'] = 'delete' in th

        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head['headers'] != '':
            return ret_head
        ret['body'] += ret_head['body']

        he = header()
        ret['body'] += he.normal()['body']

        asi = aside()
        ret['body'] += asi.normal()['body']

        ret['body'].append(('list', data))

        f = footer()
        ret['body'] += f.normal()['body']
        return ret

    def get_row(self, class_name, where: dict, condiciones: dict, urledit: str):
        get = app.get.copy()
        limit = int(get['limit']) if 'limit' in get else 10
        page = int(get['page']) if 'page' in get else 1
        search = str(get['search']) if 'search' in get else ''

        if search != '':
            condiciones['palabra'] = search

        count = class_name.getAll(where, condiciones, 'total')
        total = int(count / limit)
        if total < (count / limit):
            total += 1

        condiciones['limit'] = limit
        if page > 1:
            condiciones['limit'] = ((page - 1) * limit)
            condiciones['limit2'] = (limit)

        inicio = (limit * (page - 1)) + 1
        fin = (limit * (page))
        if fin > count:
            fin = count

        row = class_name.getAll(where, condiciones)
        for v in row:
            urltmp = urledit.copy()
            urltmp.append(v[0])
            v['url_detalle'] = functions.generar_url(urltmp)

        return {'row': row, 'page': page, 'total': total, 'limit': limit, 'search': search, 'count': count, 'inicio': inicio, 'fin': fin}

    def pagination(self, data: dict):
        import urllib.parse
        get = app.get.copy()
        limits = {
            10: {'value': 10, 'text': 10, 'active': ''},
            25: {'value': 25, 'text': 25, 'active': ''},
            100: {'value': 100, 'text': 100, 'active': ''},
            500: {'value': 500, 'text': 500, 'active': ''},
            1000: {'value': 1000, 'text': 1000, 'active': ''},
            1000000: {'value': 1000000, 'text': 'Todos', 'active': ''},
        }
        if data['limit'] in limits:
            limits[data['limit']]['active'] = 'selected'

        data['limits'] = limits.values()

        pagination = []
        rango = 5
        min = 1
        max = data['total']
        sw = False
        while ((max - min) + 1) > rango:
            if sw:
                if min != data['page'] and min + 1 != data['page']:
                    min += 1

            else:
                if max != data['page'] and max - 1 != data['page']:
                    max -= 1

            sw = not sw

        get['page'] = data['page'] - 1
        pagination.append({
            'class_page': 'previous ' + ('' if data['page'] > 1 else 'disabled'),
            'url_page': "?" + urllib.parse.urlencode(get),
            'text_page': '<i class="fa fa-angle-left"> </i> Anterior',
        })

        for i in range(min, max+1):
            get['page'] = i
            pagination.append({
                'class_page': 'active' if data['page'] == i else '',
                'url_page': "?" + urllib.parse.urlencode(get),
                'text_page': i,
            })

        get['page'] = data['page'] + 1
        pagination.append({
            'class_page': 'next ' + ('' if data['page'] < data['total'] else 'disabled'),
            'url_page': "?" + urllib.parse.urlencode(get),
            'text_page': 'Siguiente <i class="fa fa-angle-right"> </i> ',
        })

        data['pagination'] = pagination
        return data

    def field(self, th: dict, fila: dict):
        if th['field'] == '0':
            th['field'] = int(th['field'])
        if th['type'] == 'active':
            data = {
                'field': th['field'],
                'active': fila[th['field']],
                'id': fila[0],
                'class': 'btn-success' if fila[th['field']] else 'btn-danger',
                'icon': 'fa-check' if fila[th['field']] else 'fa-close',
            }

        elif th['type'] == 'color':
            if isinstance(fila[th['field']], dict):
                data = fila[th['field']]
            else:
                data = {'background': fila[th['field']], 'text': '',
                        'color': functions.getContrastColor(fila[th['field']])}

        elif th['type'] == 'delete':
            data = {'id': fila[0]}

        elif th['type'] == 'link':
            data = {'text': th['title_th'], 'url': fila[th['field']]}

        elif th['type'] == 'image':
            if th['field'] in fila and isinstance(fila[th['field']], list) and len(fila[th['field']]) > 0:
                portada = image.portada(fila[th['field']])
                thumb_url = image.generar_url(portada, 'thumb')
                zoom_url = image.generar_url(portada, 'zoom')
                original_url = image.generar_url(portada, '')
            elif isinstance(fila[th['field']], str) and fila[th['field']]!='':
                thumb_url = zoom_url = original_url = functions.ruta(fila[th['field']])
            else:
                thumb_url = zoom_url = original_url = ''
            data = {'title': th['title_th'], 'url': thumb_url,
                    'zoom': zoom_url, 'original': original_url, 'id': fila[0]}

        elif th['type'] == 'action':
            data = {'text': th['title_th'],
                    'id': fila[th['field']],
                    'action': th['action'],
                    'mensaje': th['mensaje'],
                    }

        elif th['type'] == 'text':
            return fila[th['field']]

        else:
            return fila[th['field']]

        content = ('list/'+th['type'], data)
        return content

    @staticmethod
    def configuracion(modulo: str):
        tipo_admin = str(app.session["tipo" + app.prefix_site])
        moduloconfiguracion = moduloconfiguracion_model.getByModulo(modulo)
        var = {'idmoduloconfiguracion': moduloconfiguracion[0]}
        if 'tipo' in app.get:
            var['tipo'] = app.get['tipo']
        modulo = modulo_model.getAll(var, {'limit': 1})
        modulo = modulo[0]
        estados = modulo['estado'][0]['estado']
        if 'true' != estados[tipo_admin]:
            return {'error': 301, 'redirect': functions.url_redirect(['home'])}

        th = {}
        for m in modulo['mostrar']:
            if 'true' == m['estado'][tipo_admin]:
                th[m['field']] = {'title_th': m['titulo'],
                                  'field': m['field'], 'type': m['tipo']}

        menu = {}
        for m in modulo['menu']:
            if 'true' == m['estado'][tipo_admin]:
                menu[m['field']] = True
            else:
                menu[m['field']] = False

        return {'menu': menu, 'th': th}

    @staticmethod
    def orden(class_name):
        campos = app.post['campos']
        respuesta = {'exito': False, 'mensaje': ''}
        elementos = campos['elementos']
        for e in elementos.values():
            class_name.update(e)

        respuesta['exito'] = True
        respuesta['mensaje'] = "Orden actualizado correctamente"
        return respuesta

    @staticmethod
    def estado(class_name):
        campos = app.post['campos']
        respuesta = {'exito': False, 'mensaje': ''}
        set_query = {'id': campos['id'], campos['campo']: campos['active']}
        class_name.update(set_query)
        respuesta['exito'] = True
        respuesta['mensaje'] = "Estado actualizado correctamente."
        return respuesta

    @staticmethod
    def eliminar(class_name):
        campos = app.post['campos']
        respuesta = {'exito': False, 'mensaje': ''}
        class_name.delete(campos['id'])
        respuesta['exito'] = True
        respuesta['mensaje'] = "Eliminado correctamente."
        return respuesta

    @staticmethod
    def copy(class_name):
        campos = app.post['campos']
        respuesta = {'exito': False, 'mensaje': ''}
        id = class_name.copy(campos['id'])
        respuesta['exito'] = True
        respuesta['mensaje'] = "Copiado correctamente."
        respuesta['id'] = id
        respuesta['refresh'] = True
        return respuesta

    @staticmethod
    def excel(class_name, where, select, title):
        respuesta = {'exito': False, 'mensaje': 'No hay datos para exportar'}
        condiciones = {}
        condiciones['limit'] = app.post['limit']
        condiciones['limit2'] = app.post['limit2']
        row = class_name.getAll(where, condiciones, select)
        if len(row) > 0:
            head = []
            delete = []
            for k, v in row[0].items():
                if isinstance(v, dict) or isinstance(k, int) or 'tipo' == k or 'orden' == k or 'estado' == k or k == class_name.idname:
                    delete.append(k)
                else:
                    head.append(k)

            if len(delete) > 0:
                for r in row:
                    for d in delete:
                        del r[d]

            respuesta['exito'] = True
            respuesta['mensaje'] = "Excel generado."
            respuesta['exportar'] = row
            respuesta['head'] = head
            respuesta['title'] = title

        return respuesta
