from core.app import app
from core.email import email
from core.functions import functions

from .base import base

from email.utils import parseaddr
import urllib.request
import json


class enviar(base):
    def index(self):
        ret = {
            "headers": [("Content-Type", "application/json charset=utf-8")],
            "body": "",
        }
        campos = app.post["campos"]
        respuesta = {"exito": True, "mensaje": ""}
        nombre_sitio = app.title
        config = app.get_config()
        secret = config["google_captcha_secret"]
        email_empresa = config["main_email"]

        if campos["nombre"] == "":
            respuesta["mensaje"] += "<strong>Error!</strong>&nbsp Nombre vacío.<br/>"

        if campos["email"] == "":
            respuesta["mensaje"] += "<strong>Error!</strong>&nbsp Email vacío.<br/>"
        elif "@" not in parseaddr(campos["email"])[1]:
            respuesta["mensaje"] += "<strong>Error!</strong>&nbsp Email no valido.<br/>"

        if campos["mensaje"] == "":
            respuesta["mensaje"] += "<strong>Error!</strong>&nbsp Mensaje vacío.<br/>"

        if "g-recaptcha-response" not in campos or campos["g-recaptcha-response"] == "":
            respuesta[
                "mensaje"
            ] += "<strong>Error!</strong>&nbsp Error en captcha. Por favor completa el captcha.<br/>"
            respuesta["captcha"] = True

        if respuesta["mensaje"] != "":
            respuesta["exito"] = False

        if respuesta["exito"]:
            url = "https://www.google.com/recaptcha/api/siteverify?secret={}&response={}&remoteip={}"
            url = url.format(secret, campos["g-recaptcha-response"], app.client_ip)

            file = urllib.request.urlopen(url)
            captcha = json.loads(file)
            respuesta["exito"] = captcha["success"]
            if not respuesta["exito"]:
                respuesta[
                    "mensaje"
                ] = "<strong>Error!</strong>&nbsp Error en captcha. Por favor completa el captcha."

            respuesta["captcha"] = True
            del campos["g-recaptcha-response"]

        if respuesta["exito"]:
            body_email = {
                "template": "contacto",
                "titulo": "Formulario de " + campos["titulo"],
                "cabecera": "Estimado {}, hemos recibido su correo, el cual será respondido a la brevedad por el centro de atención al cliente de {}".format(
                    campos["nombre"], nombre_sitio
                ),
            }
            titulo = campos["titulo"]
            body_email["campos_largos"] = {
                "Mensaje": campos["mensaje"].replace("\n", "<br>\n")
            }
            del campos["accion"]
            del campos["titulo"]
            del campos["mensaje"]
            body_email["campos"] = campos
            imagenes = []

            adjuntos = []
            if "file" in app.post:
                for file in app.post["file"]:
                    adjuntos.append(
                        {"archivo": file["tmp_name"], "nombre": file["name"]}
                    )

            body = email.body_email(body_email)
            respuesta = email.enviar_email(
                [campos["email"], email_empresa],
                "Formulario de " + titulo,
                body,
                adjuntos,
                imagenes,
            )

            if respuesta["exito"]:
                respuesta[
                    "mensaje"
                ] = "<strong>Gracias!</strong>&nbsp Email enviado correctamente."
                respuesta["captcha"] = True
            else:
                respuesta["mensaje"] = (
                    "<strong>Error!</strong>&nbsp No se puede enviar el email, por favor intente más tarde.<br/>"
                    + respuesta["mensaje"]
                )
                respuesta["captcha"] = True

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret

