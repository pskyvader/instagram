from core.view import view
from core.cache import cache


class static:
    def init(self, var):
        if len(var) == 0:
            return {'error': 404}
        theme = view.get_theme()
        resource = '/'.join(var)
        print(resource)
        resource_url = theme + resource
        ret=cache.serve_cache(resource_url,theme,resource)
        return ret
