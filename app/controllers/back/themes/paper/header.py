from core.functions import functions
from core.app import app
from core.image import image
from app.models.logo import logo as logo_model


class header:
    data = {'logo': '', 'url_exit': '', }

    def normal(self):
        ret = {'body': []}
        if 'ajax' not in app.post:
            logo = logo_model.getById(3)
            portada=image.portada(logo['foto'])
            self.data['logo_max'] = image.generar_url(portada, 'panel_max')
            logo = logo_model.getById(4)
            portada=image.portada(logo['foto'])
            self.data['logo_min'] = image.generar_url(portada, 'panel_min')
            self.data['url_exit'] = functions.generar_url(['logout'], False)
            self.data['date'] = functions.current_time()
            ret['body'].append(('header', self.data))
        return ret
