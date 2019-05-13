from core.functions import functions
from core.app import app
from core.image import image
from app.models.administrador import administrador as administrador_model
from app.models.logo import logo as logo_model
from .head import head
from .footer import footer
from .base import base


class recuperar(base):
    url = ['recuperar', 'index']
    metadata = {'title': 'Recuperar Contraseña', 'modulo': 'recuperar'}

    @classmethod
    def index(cls, var):
        from time import time
        url = var
        ret = {'body': []}
        url_final = cls.url.copy()
        url_final = url_final+url



        if 'bloqueo_recuperar' in app.session and app.session['bloqueo_recuperar'] > time():
            ret['body'] = "IP Bloqueada por intentos fallidos. Intente más tarde. tiempo: " +  str(int( app.session['bloqueo_recuperar']-time()))+" segundos"
            return ret

        if 'intento_bloqueo' in app.session and int(app.session['intento_bloqueo']) % 5 == 0:
            app.session['bloqueo_recuperar'] = time( ) + 60*int(app.session['intento_bloqueo'])
            # if app.session['intento_bloqueo']>=15) bloquear_ip(getRealIP())
            #app.session['intento_bloqueo'] += 1

        error_recuperar = False
        exito=False
        if 'email' in app.post and 'token' in app.post:
            if 'recuperar_token' in app.session:
                if app.session['recuperar_token']['token'] == app.post['token']:
                    if time()-int(app.session['recuperar_token']['time']) <= 120:
                        recuperar = administrador_model.recuperar(app.post['email'])
                        if recuperar:
                            if 'intento_bloqueo' in app.session:
                                app.session['intento_bloqueo'] = 0
                            exito=True
                        else:
                            error_recuperar = True
                            if not 'intento_bloqueo' in app.session:
                                app.session['intento_bloqueo'] = 1
                            app.session['intento_bloqueo'] += 1
                    else:
                        error_recuperar = True
                else:
                    error_recuperar = True
            else:
                error_recuperar = True
                if not 'intento_bloqueo' in app.session:
                    app.session['intento_bloqueo'] = 0
                app.session['intento_bloqueo'] += 5

        url_return = functions.url_redirect(url_final)
        if url_return != '':
            ret['error'] = 301
            ret['redirect'] = url_return
            return ret

        token = functions.generar_pass(20)
        app.session['recuperar_token'] = {'token': token, 'time': time()}
        h = head(cls.metadata)
        ret_head = h.normal()
        if ret_head['headers'] != '':
            return ret_head
        ret['body'] += ret_head['body']

        data = {}
        data['error_recuperar'] = error_recuperar
        data['exito'] = exito
        data['token'] = token
        data['url_login'] = functions.generar_url(["login","index"])
        logo = logo_model.getById(2)
        data['logo'] = image.generar_url(logo['foto'][0], 'login')
        ret['body'].append(('recuperar', data))

        f = footer()
        ret['body'] += f.normal()['body']

        return ret
