from core.functions import functions
from core.view import view
import json


class sw():
    def init(self, var=[]):
        ret = {'headers': [ ('Content-Type', 'application/javascript; charset=utf-8')], 'body': []}

        version_application = 1

        lista_cache = []
        lista_cache.append(functions.generar_url( ["application", "index", version_application], False))

        # array(css,fecha modificacion mas reciente)
        css = view.css(True, True)
        # array(js,fecha modificacion mas reciente)
        js = view.js(True, True)

        for c in css[0]:
            lista_cache.append(c['url'])

        for j in js[0]:
            lista_cache.append(j['url'])

        data = {}
        data['lista_cache'] = json.dumps(lista_cache)
        data['cache'] = True
        data['version'] = str(js[1])+'-'+str(css[1])

        ret['body'].append(('sw', data))
        return ret
