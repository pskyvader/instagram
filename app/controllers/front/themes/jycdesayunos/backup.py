from core.app import app
from core.cache import cache


class backup:
    def init(self, var):
        if len(var) == 0:
            return {'error': 404}
        theme =  app.get_dir(True)+'backup/'
        resource = '/'.join(var)
        resource_url = theme + resource
        ret=cache.serve_cache(resource_url,theme,resource)
        return ret
