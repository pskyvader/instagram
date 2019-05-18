from core.app import app
from core.cache import cache


class uploads:
    def init(self, var):
        if len(var) == 0:
            return {'error': 404}
        theme =  app.get_dir(True)+'uploads/'
        resource = '/'.join(var)
        print(resource)
        resource_url = theme + resource
        ret=cache.serve_cache(resource_url,theme,resource)
        return ret
