from core.view import view
from core.app import app


class footer:
    def normal(self):
        ret = {'body': []}
        if 'ajax' not in app.post:
            data = {}
            data['js'] = view.js()
            ret['body'].append(('footer', data))
        return ret
