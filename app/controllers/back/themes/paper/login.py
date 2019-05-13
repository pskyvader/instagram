from core.functions import functions
from core.app import app
from core.image import image
from app.models.administrador import administrador as administrador_model
from app.models.logo import logo as logo_model
from .head import head
from .footer import footer
from .base import base


class login(base):
    url = ['login', 'index']
    metadata = {'title': 'login', 'modulo': 'login'}

    @classmethod
    def index(cls, var):
        from time import time
        url = var
        ret = {'body': []}
        url_final = cls.url.copy()
        url_final = url_final+url

        cookie_admin = functions.get_cookie('cookieadmin'+app.prefix_site)
        if cookie_admin != False:
            logueado = administrador_model.login_cookie(cookie_admin)
            if logueado:
                if not url:
                    url_final = ['home']
                else:
                    url_final = url
        if 'bloqueo_administrador' in app.session and app.session['bloqueo_administrador'] > time():
            ret['body'] = "IP Bloqueada por intentos fallidos. Intente más tarde. tiempo: " + \
                str(int(
                    app.session['bloqueo_administrador']-time()))+" segundos"
            return ret

        if 'intento_administrador' in app.session and int(app.session['intento_administrador']) % 5 == 0:
            app.session['bloqueo_administrador'] = time(
            ) + 60*int(app.session['intento_administrador'])
            # if app.session['intento_administrador']>=15) bloquear_ip(getRealIP())
            #app.session['intento_administrador'] += 1

        error_login = False
        if 'email' in app.post and 'pass' in app.post and 'token' in app.post:
            if 'login_token' in app.session:
                if app.session['login_token']['token'] == app.post['token']:
                    if time()-int(app.session['login_token']['time']) <= 120:
                        if not 'recordar' in app.post:
                            app.post['recordar'] = ''
                        logueado = administrador_model.login(
                            app.post['email'], app.post['pass'], app.post['recordar'])
                        if logueado:
                            if 'intento_administrador' in app.session:
                                app.session['intento_administrador'] = 0
                            if not url:
                                url_final = ['home']
                            else:
                                url_final = url
                        else:
                            error_login = True
                            if not 'intento_administrador' in app.session:
                                app.session['intento_administrador'] = 1
                            app.session['intento_administrador'] += 1
                    else:
                        error_login = True
                else:
                    error_login = True
            else:
                error_login = True
                if not 'intento_administrador' in app.session:
                    app.session['intento_administrador'] = 0
                app.session['intento_administrador'] += 5

        url_return = functions.url_redirect(url_final)
        if url_return != '':
            ret['error'] = 301
            ret['redirect'] = url_return
            return ret

        token = functions.generar_pass(20)
        app.session['login_token'] = {'token': token, 'time': time()}
        h = head(cls.metadata)
        ret_head = h.normal()
        if ret_head['headers'] != '':
            return ret_head
        ret['body'] += ret_head['body']

        data = {}
        data['error_login'] = error_login
        data['token'] = token
        data['url_recuperar'] = functions.generar_url(["recuperar","index"])
        logo = logo_model.getById(2)
        data['logo'] = image.generar_url(logo['foto'][0], 'login')
        ret['body'].append(('login', data))

        f = footer()
        ret['body'] += f.normal()['body']

        return ret
