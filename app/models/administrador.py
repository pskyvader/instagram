from core.database import database
from .base_model import base_model
from .log import log
from .table import table
from .profile import profile as profile_model
from core.app import app
from core.functions import functions


class administrador(base_model):
    idname = 'idadministrador'
    table = 'administrador'

    @classmethod
    def insert(cls, set_query,  loggging=True):
        if 'pass' in set_query and set_query['pass'] != '':
            if 'pass_repetir' in set_query and set_query['pass_repetir'] != '':
                if set_query['pass'] != set_query['pass_repetir']:
                    return {'exito': False, 'mensaje': 'Contraseñas no coinciden'}
            else:
                return {'exito': False, 'mensaje': 'Contraseña no existe'}
        else:
            return {'exito': False, 'mensaje': 'Contraseña no existe'}

        fields     = table.getByname(cls.table)
        insert = database.create_data(fields, set_query)
        insert['pass'] = database.encript(insert['pass'])
        insert['email'] = insert['email'].lower()

        connection = database.instance()
        row = connection.insert(cls.table, cls.idname, insert)
        if isinstance(row, int) and row > 0:
            last_id = row
            if loggging:
                log.insert_log(cls.table, cls.idname, cls, insert)
                pass
            return last_id
        else:
            return row

    @classmethod
    def update(cls, set_query, loggging=True):

        if 'id' not in set_query or set_query['id'] == '' or set_query['id'] == 0:
            print('Error, ID perdida')
            return False

        if 'pass' in set_query and set_query['pass'] != '':
            if 'pass_repetir' in set_query and set_query['pass_repetir'] != '':
                if set_query['pass'] != set_query['pass_repetir']:
                    return {'exito': False, 'mensaje': 'Contraseñas no coinciden'}
                else:
                    set_query['pass'] = database.encript(set_query['pass'])
                    set_query['cookie'] = ''
                    del set_query['pass_repetir']

            else:
                return {'exito': False, 'mensaje': 'Contraseña no existe'}
        else:
            if 'pass' in set_query:
                del set_query['pass']
            if 'pass_repetir' in set_query:
                del set_query['pass_repetir']

        if 'email' in set_query:
            set_query['email'] = set_query['email'].lower()

        where = {cls.idname: set_query['id']}
        del set_query['id']
        connection = database.instance()
        row = connection.update(cls.table, cls.idname, set_query, where)
        if loggging:
            log_register=set_query
            log_register.update(where)
            log.insert_log(cls.table, cls.idname, cls, log_register)
        if isinstance(row, bool) and row:
            row = where[cls.idname]
        return row

    @staticmethod
    def login_cookie(cookie):
        prefix_site = app.prefix_site
        where = {'cookie': cookie}
        condiciones = {'limit': 1}
        row = administrador.getAll(where, condiciones)

        if len(row) == 1:
            admin = row[0]
            if admin['estado']:
                profile = profile_model.getByTipo(admin['tipo'])
                if 'tipo' in profile and int(profile['tipo']) > 0:
                    session = app.session
                    session[administrador.idname + prefix_site] = admin[0]
                    session["email" + prefix_site] = admin['email']
                    session["nombre" + prefix_site] = admin['nombre']
                    session["estado" + prefix_site] = admin['estado']
                    session["tipo" + prefix_site] = admin['tipo']
                    log.insert_log(administrador.table, administrador.idname, administrador, admin)
                    return True
        functions.set_cookie(cookie, 'aaa', (31536000))
        return False

    @staticmethod
    def login(email, password, recordar):
        prefix_site = app.prefix_site
        if email == '' or password == '':
            return False

        where = {'email': email.lower(), 'pass': database.encript(password)}
        condiciones = {'limit': 1}
        row = administrador.getAll(where, condiciones)

        if len(row) != 1:
            return False
        else:
            admin = row[0]
            if not admin['estado']:
                return False
            else:
                profile = profile_model.getByTipo(admin['tipo'])
                if not 'tipo' in profile or int(profile['tipo']) <= 0:
                    return False
                else:
                    session = app.session
                    session[administrador.idname + prefix_site] = admin[0]
                    session["email" + prefix_site] = admin['email']
                    session["nombre" + prefix_site] = admin['nombre']
                    session["estado" + prefix_site] = admin['estado']
                    session["tipo" + prefix_site] = admin['tipo']
                    session['prefix_site'] = prefix_site
                    log.insert_log(administrador.table, administrador.idname, administrador, admin)
                    if recordar == 'on':
                        return administrador.update_cookie(admin[0])
                    else:
                        return True

    @staticmethod
    def update_cookie(id_cookie):
        import uuid
        cookie = uuid.uuid4().hex
        data = {'id': id_cookie, 'cookie': cookie}
        exito = administrador.update(data)
        if exito:
            functions.set_cookie('cookieadmin' + app.prefix_site, cookie, (31536000))

        return exito

    @staticmethod
    def logout():
        prefix_site = app.prefix_site
        session = app.session
        if administrador.idname + prefix_site in session:
            del session[administrador.idname + prefix_site]
            del session["email" + prefix_site]
            del session["nombre" + prefix_site]
            del session["estado" + prefix_site]
            del session["tipo" + prefix_site]
            
        functions.set_cookie('cookieadmin' + prefix_site, 'aaa', (31536000))

    @staticmethod
    def verificar_sesion():
        prefix_site = app.prefix_site
        session = app.session
        if (administrador.idname+prefix_site) in session and session[administrador.idname + prefix_site] != '':
            admin = administrador.getById(
                session[administrador.idname + prefix_site])
            if 0 in admin and admin[0] != session[administrador.idname + prefix_site]:
                return False
            elif admin['email'] != session["email" + prefix_site]:
                return False
            elif admin['estado'] != session["estado" + prefix_site] or not session["estado" + prefix_site]:
                return False
            elif admin['tipo'] != session["tipo" + prefix_site] or not session["tipo" + prefix_site]:
                return False
            else:
                profile = profile_model.getByTipo(admin['tipo'])
                if not 'tipo' in profile or int(profile['tipo']) <= 0:
                    return False
                else:
                    return True

        cookie = functions.get_cookie()
        if 'cookieadmin' + prefix_site in cookie and cookie['cookieadmin' + prefix_site] != '' and cookie['cookieadmin' + prefix_site] != 'aaa':
            return administrador.login_cookie(cookie['cookieadmin' + prefix_site])

        return False

    @staticmethod
    def recuperar(email_recuperar):
        """recuperar contraseña"""
        from core.view import view
        from core.email import email
        nombre_sitio = app.title
        if email_recuperar == '':
            return False

        where = {'email': email_recuperar.lower()}
        condiciones = {'limit': 1}
        row = administrador.getAll(where, condiciones)

        if len(row) != 1:
            return False
        else:
            admin = row[0]
            if not admin['estado']:
                return False
            else:
                password = functions.generar_pass()
                data = {'id': admin[0], 'pass': password, 'pass_repetir': password}
                row = administrador.update(data,False)

                if row:
                    body_email = {
                        'template': 'recuperar_password',
                        'titulo': "Recuperación de contraseña",
                        'cabecera': "Estimado " + admin["nombre"] + ", se ha solicitado la recuperación de contraseña en " + nombre_sitio,
                        'campos': {'Contraseña (sin espacios)': password},
                        'campos_largos': {},
                    }
                    body = email.body_email(body_email)
                    respuesta = email.enviar_email([email_recuperar], 'Recuperación de contraseña', body)
                    log.insert_log(administrador.table, administrador.idname, administrador, admin)
                    return respuesta['exito']
                else:
                    return False
