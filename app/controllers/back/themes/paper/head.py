from core.app import app
from core.functions import functions
from core.view import view
from core.image import image
from app.models.logo import logo as logo_model
import json


class head:
    data = {
        'favicon': '',
        'keywords': '',
        'description': '',
        'title': '',
        'current_url': '',
        'image': '',
        'color_primario': '',
        'manifest_url': '',
        'path': '',
        'modulo': '',
        'max_size': -1,
    }

    def __init__(self, metadata):
        for key, value in metadata.items():
            if key in self.data:
                head.data[key] = value

        config = app.get_config()
        head.data['current_url'] = functions.current_url()
        head.data['path'] = app.path
        head.data['color_primario'] = config['color_primario']
        head.data['googlemaps_key'] = config['googlemaps_key']
        # size=functions::get_max_size()
        #head.data['max_size'] = size
        # head.data['max_size_format'] = (size<0)?"Ilimitado":functions::file_size(size,true)}
        head.data['websocket_url']='ws://'+app.root_url +':8001'

        titulo = head.data['title'] + ' - ' + config['title']
        if (len(titulo) > 75):
            titulo = head.data['title'] + ' - ' + config['short_title']

        if (len(titulo) > 75):
            titulo = head.data['title']

        if (len(titulo) > 75):
            titulo = head.data['title'][0:75]

        head.data['title'] = titulo

        if 'image' in metadata and metadata['image'] != '':
            head.data['image'] = metadata['image']
        else:
            logo = logo_model.getById(3)
            head.data['image'] = image.generar_url(
                logo['foto'][0], 'panel_max')

        logo = logo_model.getById(1)
        head.data['favicon'] = image.generar_url(logo['foto'][0], 'favicon')

        head.data['manifest_url'] = app.get_url() + 'manifest.js'

    def normal(self):
        ret = {'headers': '', 'body': []}
        if 'ajax' not in app.post:
            if 'ajax_header' not in app.post:
                head.data['css'] = view.css()
                ret['body'].append(('head', head.data))
            else:
                ret['headers'] = [
                    ('Content-Type', 'application/json; charset=utf-8')]
                ret['body'] = json.dumps(self.data,ensure_ascii=False)
        return ret
