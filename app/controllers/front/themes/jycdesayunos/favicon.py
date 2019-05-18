from core.app import app
from core.cache import cache
from core.image import image
from app.models.logo import logo as logo_model



class favicon:
    def init(self, var):
        logo=logo_model.getById(1)
        portada=image.portada(logo['foto'])
        theme =  app.get_dir(True)+'uploads/'
        resource_url = image.generar_dir(portada, 'favicon')
        resource = resource_url[len(theme):]
        print(theme,resource)
        ret=cache.serve_cache(resource_url,theme,resource)
        return ret
