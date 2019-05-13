from core.app import app
from pathlib import Path
import os
import mimetypes


class static_file:
    def init(self, var=[]):
        if len(var) > 0:
            resource_url = app.get_dir(True)+var[0]
            mime = mimetypes.guess_type(resource_url, False)[0]
            if mime == None:
                mime = 'text/plain'
            ret = {
                'headers': [('Content-Type', mime+'; charset=utf-8')],
                'body': '',
                'is_file': True,
                'file': resource_url
            }

            my_file = Path(resource_url)
            if not my_file.is_file():
                open(resource_url, 'w+').close()
            return ret
        else:
            ret = {
                'error': 404
            }
            return ret
