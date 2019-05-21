from core.app import app
from core.functions import functions
from .base import base
from .head import head
from .header import header
from .aside import aside
from .footer import footer
from app.models.administrador import administrador as administrador_model
from app.models.igaccounts import igaccounts as igaccounts_model
from app.models.ighashtag import ighashtag as ighashtag_model

import json


class home(base):
    url = ['home']
    metadata = {'title': 'Home', 'modulo': 'home'}

    @classmethod
    def index(cls):
        ret = {'body': []}
        url_final = cls.url.copy()
        if not administrador_model.verificar_sesion():
            url_final = ['login', 'index', 'home']

        url_return = functions.url_redirect(url_final)
        if url_return != '':
            ret['error'] = 301
            ret['redirect'] = url_return
            return ret

        h = head(cls.metadata)
        ret_head = h.normal()
        if ret_head['headers'] != '':
            return ret_head
        ret['body'] += ret_head['body']

        he = header()
        ret['body'] += he.normal()['body']

        asi = aside()
        ret['body'] += asi.normal()['body']
        data = {}
        data['title'] = cls.metadata['title']
        cls.breadcrumb = [{'url': functions.generar_url(
            url_final), 'title': cls.metadata['title'], 'active':'active'}]
        data['breadcrumb'] = cls.breadcrumb
        ret['body'].append(('home', data))

        f = footer()
        ret['body'] += f.normal()['body']

        return ret


    
    def get_followers(self):
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {}
        # respuesta['total']=igaccounts_model.getAll(select='total')
        where={'follower':True}
        respuesta['follower']=igaccounts_model.getAll(where,select='total')
        where={'following':True}
        respuesta['following']=igaccounts_model.getAll(where,select='total')
        where={'follower':True,'following':True}
        respuesta['both']=igaccounts_model.getAll(where,select='total')
        where={'favorito':True}
        respuesta['favoritos']=igaccounts_model.getAll(where,select='total')
        # where={'favorito':True,'follower':True}
        # respuesta['favoritos-follower']=igaccounts_model.getAll(where,select='total')
        # where={'favorito':True,'following':True}
        # respuesta['favoritos-following']=igaccounts_model.getAll(where,select='total')
        # where={'favorito':True,'follower':True,'following':True}
        # respuesta['favoritos-follower-following']=igaccounts_model.getAll(where,select='total')
        

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret


    def get_hashtag_users(self):
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {}
        respuesta['total']=igaccounts_model.getAll(select='total')
        hashtag=ighashtag_model.getAll()
        for h in hashtag:
            respuesta[h['hashtag']]=igaccounts_model.getAll({'hashtag':h['hashtag']},select='total')

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret
