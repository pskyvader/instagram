from core.database import database
from .base_model import base_model
from .log import log
from .table import table
from .profile import profile as profile_model
from core.app import app
from core.functions import functions


class usuario(base_model):
    idname = "idusuario"
    table = "usuario"

    @classmethod
    def insert(cls, set_query, loggging=True):
        if "pass" in set_query and set_query["pass"] != "":
            if "pass_repetir" in set_query and set_query["pass_repetir"] != "":
                if set_query["pass"] != set_query["pass_repetir"]:
                    return {"exito": False, "mensaje": "Contraseñas no coinciden"}
            else:
                return {"exito": False, "mensaje": "Contraseña no existe"}
        else:
            return {"exito": False, "mensaje": "Contraseña no existe"}

        fields = table.getByname(cls.table)
        insert = database.create_data(fields, set_query)
        insert["pass"] = database.encript(insert["pass"])
        insert["email"] = insert["email"].lower()

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

        if "id" not in set_query or set_query["id"] == "" or set_query["id"] == 0:
            print("Error, ID perdida")
            return False

        if "pass" in set_query and set_query["pass"] != "":
            if "pass_repetir" in set_query and set_query["pass_repetir"] != "":
                if set_query["pass"] != set_query["pass_repetir"]:
                    return {"exito": False, "mensaje": "Contraseñas no coinciden"}
                else:
                    set_query["pass"] = database.encript(set_query["pass"])
                    set_query["cookie"] = ""
                    del set_query["pass_repetir"]

            else:
                return {"exito": False, "mensaje": "Contraseña no existe"}
        else:
            if "pass" in set_query:
                del set_query["pass"]
            if "pass_repetir" in set_query:
                del set_query["pass_repetir"]

        if "email" in set_query:
            set_query["email"] = set_query["email"].lower()

        where = {cls.idname: set_query["id"]}
        del set_query["id"]
        connection = database.instance()
        row = connection.update(cls.table, cls.idname, set_query, where)
        if loggging:
            log_register = set_query
            log_register.update(where)
            log.insert_log(cls.table, cls.idname, cls, log_register)
        if isinstance(row, bool) and row:
            row = where[cls.idname]
        return row

    @staticmethod
    def login_cookie(cookie):
        prefix_site = app.prefix_site
        where = {"cookie": cookie}
        condiciones = {"limit": 1}
        row = usuario.getAll(where, condiciones)

        if len(row) == 1:
            user = row[0]
            if user["estado"]:
                profile = profile_model.getByTipo(user["tipo"])
                if "tipo" in profile and int(profile["tipo"]) > 0:
                    session = app.session
                    session[usuario.idname + prefix_site] = user[0]
                    session["emailusuario" + prefix_site] = user["email"]
                    session["nombreusuario" + prefix_site] = user["nombre"]
                    session["estadousuario" + prefix_site] = user["estado"]
                    session["tipousuario" + prefix_site] = user["tipo"]
                    log.insert_log(usuario.table, usuario.idname, usuario, user)
                    return True
        functions.set_cookie(cookie, "aaa", (31536000))
        return False

    @staticmethod
    def login(email, password, recordar):
        prefix_site = app.prefix_site
        if email == "" or password == "":
            return False

        where = {"email": email.lower(), "pass": database.encript(password)}
        condiciones = {"limit": 1}
        row = usuario.getAll(where, condiciones)

        if len(row) != 1:
            return False
        else:
            user = row[0]
            if not user["estado"]:
                return False
            else:
                profile = profile_model.getByTipo(user["tipo"])
                if not "tipo" in profile or int(profile["tipo"]) <= 0:
                    return False
                else:
                    session = app.session
                    session[usuario.idname + prefix_site] = user[0]
                    session["emailusuario" + prefix_site] = user["email"]
                    session["nombreusuario" + prefix_site] = user["nombre"]
                    session["estadousuario" + prefix_site] = user["estado"]
                    session["tipousuario" + prefix_site] = user["tipo"]
                    log.insert_log(usuario.table, usuario.idname, usuario, user)
                    if recordar == "on":
                        return usuario.update_cookie(user[0])
                    else:
                        return True

    @classmethod
    def registro(
        cls,
        nombre: str,
        telefono: str,
        email: str,
        password: str,
        password_repetir: str,
    ):
        respuesta = {"exito": False, "mensaje": ""}
        if nombre == "" or email == "" or password == "" or password_repetir == "":
            respuesta["mensaje"] = "Todos los datos son obligatorios"
            return respuesta

        where = {"email": email.lower()}
        condiciones = {"limit": 1}
        row = cls.getAll(where, condiciones)

        if len(row) > 0:
            respuesta[
                "mensaje"
            ] = "Este email ya existe. Puede recuperar la contraseña en el boton correspondiente"
        else:
            data = {
                "nombre": nombre,
                "telefono": telefono,
                "email": email,
                "pass": password,
                "pass_repetir": password_repetir,
                "tipo": 1,
                "estado": True,
            }
            id = cls.insert(data)
            if not isinstance(id, list):
                respuesta["exito"] = True
            else:
                respuesta = id

        return respuesta

    @classmethod
    def actualizar(cls, datos: dict):
        respuesta = {"exito": False, "mensaje": ""}
        if datos["nombre"] == "" or datos["telefono"] == "" or datos["email"] == "":
            respuesta["mensaje"] = "Todos los datos son obligatorios"
            return respuesta

        usuario = cls.getById(app.session[cls.idname + app.prefix_site])

        if usuario["email"] != datos["email"]:
            where = {"email": datos["email"].lower()}
            condiciones = {"limit": 1}
            row = cls.getAll(where, condiciones)
            if len(row) > 0:
                respuesta[
                    "mensaje"
                ] = "Este email ya existe. No puedes modificar tu email."
                return respuesta
            else:
                respuesta["redirect"] = True

        datos["id"] = usuario[0]
        id = cls.update(datos)
        if not isinstance(id,int) and "exito" in id:
            respuesta = id
        else:
            respuesta["exito"] = True

        return respuesta

    @staticmethod
    def update_cookie(id_cookie):
        import uuid

        cookie = uuid.uuid4().hex
        data = {"id": id_cookie, "cookie": cookie}
        exito = usuario.update(data)
        if exito:
            functions.set_cookie("cookieusuario" + app.prefix_site, cookie, (31536000))

        return exito

    @staticmethod
    def logout():
        prefix_site = app.prefix_site
        session = app.session
        del session[usuario.idname + prefix_site]
        del session["emailusuario" + prefix_site]
        del session["nombreusuario" + prefix_site]
        del session["estadousuario" + prefix_site]
        del session["tipousuario" + prefix_site]
        del session["cookie_pedido" + prefix_site]
        functions.set_cookie("cookieusuario" + prefix_site, "aaa", (31536000))

    @staticmethod
    def verificar_sesion():
        prefix_site = app.prefix_site
        session = app.session
        if (usuario.idname + prefix_site) in session and session[
            usuario.idname + prefix_site
        ] != "":
            user = usuario.getById(session[usuario.idname + prefix_site])
            if 0 in user and user[0] != session[usuario.idname + prefix_site]:
                return False
            elif user["email"] != session["emailusuario" + prefix_site]:
                return False
            elif (
                user["estado"] != session["estadousuario" + prefix_site]
                or not session["estadousuario" + prefix_site]
            ):
                return False
            elif (
                user["tipo"] != session["tipousuario" + prefix_site]
                or not session["tipousuario" + prefix_site]
            ):
                return False
            else:
                return True

        cookie = functions.get_cookie()
        if (
            "cookieusuario" + prefix_site in cookie
            and cookie["cookieusuario" + prefix_site] != ""
            and cookie["cookieusuario" + prefix_site] != "aaa"
        ):
            return usuario.login_cookie(cookie["cookieusuario" + prefix_site])

        return False

    @staticmethod
    def recuperar(email):
        """recuperar contraseña"""
        from core.view import view

        respuesta = {"exito": False, "mensaje": ""}
        nombre_sitio = app.title
        if email == "":
            respuesta["mensaje"] = "Debes llenar tu email"
            return respuesta

        where = {"email": email.lower()}
        condiciones = {"limit": 1}
        row = usuario.getAll(where, condiciones)

        if len(row) < 1:
            respuesta[
                "mensaje"
            ] = "Este email no existe, puedes registrarte en el link correspondiente"
            return respuesta
        else:
            user = row[0]
            if not user["estado"]:
                respuesta[
                    "mensaje"
                ] = "Tu usuario existe pero ha sido desactivado. Por favor envia un mensaje en el formulario de contacto."
                return respuesta
            else:
                password = functions.generar_pass()
                data = {"id": user[0], "pass": password, "pass_repetir": password}
                row = usuario.update(data)

                if row:
                    body_email = {
                        "body": view.get_theme() + "mail/recuperar_password.html",
                        "titulo": "Recuperación de contraseña",
                        "cabecera": "Estimado "
                        + user["nombre"]
                        + ", se ha solicitado la recuperación de contraseña en "
                        + nombre_sitio,
                        "campos": {"Contraseña (sin espacios)": password},
                        "campos_largos": {},
                    }
                    body = email.body_email(body_email)
                    respuesta = email.enviar_email(
                        [email], "Recuperación de contraseña", body
                    )

                    log.insert_log(usuario.table, usuario.idname, usuario, user)
                    return respuesta
                else:
                    return False
