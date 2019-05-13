from app.models.logo import logo as logo_model

from .app import app
from .image import image
from .view import view

import smtplib
import os.path as op
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import COMMASPACE, formatdate
from email import encoders


class email:
    @staticmethod
    def body_email(body_email, data={}):
        config = app.get_config()
        data["dominio"] = config["domain"]
        data["email_empresa"] = config["main_email"]
        data["email_from"] = config["email_from"]
        data["nombre_sitio"] = config["title"]
        data["color_primario"] = config["color_primario"]
        data["color_secundario"] = config["color_secundario"]
        data["logo"] = "cid:logo"
        data["titulo"] = body_email["titulo"]
        data["cabecera"] = body_email["cabecera"]
        data["campos"] = body_email["campos"]
        data["campos_largos"] = body_email["campos_largos"]

        template = body_email["template"]
        body = view.render([(template, data)], True, view.get_theme() + "mail/")

        return body

    @staticmethod
    def enviar_email(email_destino, asunto, body, adjuntos=[], imagenes=[]):
        config = app.get_config()
        email_from = config["email_from"]
        nombre_sitio = config["title"]

        # send_from = nombre_sitio + ', ' + asunto + " <"+email_from+">"
        send_from = email_from

        smtp = {}
        if config["email_smtp"] != "":
            smtp["debug"] = config["email_debug"]
            smtp["host"] = config["email_host"]
            smtp["port"] = config["email_port"]
            smtp["email"] = config["email_smtp"]
            smtp["user"] = config["email_user"]
            smtp["pass"] = config["email_pass"]

        logo = logo_model.getById(8)
        logo = image.portada(logo["foto"])
        imagenes.append({"url": image.generar_dir(logo, "email"), "tag": "logo"})

        if config["email_smtp"] != "":
            respuesta = email.send_mail(
                send_from,
                email_destino,
                asunto,
                body,
                adjuntos,
                imagenes,
                smtp["host"],
                smtp["port"],
                smtp["user"],
                smtp["pass"],
            )
        else:
            respuesta = email.send_mail(
                send_from, email_destino, asunto, body, adjuntos, imagenes
            )
        return respuesta

    @staticmethod
    def send_mail(
        send_from,
        send_to,
        subject,
        message,
        files=[],
        images=[],
        server="localhost",
        port=587,
        username="",
        password="",
        use_tls=True,
    ):
        """Compose and send email with provided info and attachments.

        Args:
            send_from (str): from name
            send_to (str): to name
            subject (str): message title
            message (str): message body
            files (list[str]): list of file paths to be attached to email
            server (str): mail server host name
            port (int): port number
            username (str): server auth username
            password (str): server auth password
            use_tls (bool): use TLS mode
        """

        respuesta = {"exito": False, "mensaje": ""}
        msg = MIMEMultipart()
        msg["From"] = send_from
        msg["To"] = COMMASPACE.join(send_to)
        msg["Date"] = formatdate(localtime=True)
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "html"))

        for file in files:
            path = file["archivo"]
            filename = file["nombre"]
            # filename=op.basename(path)
            part = MIMEBase("application", "octet-stream")
            if isinstance(path, str):
                with open(path, "rb") as file:
                    part.set_payload(file.read())
            else:
                part.set_payload(path.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition", 'attachment filename="{}"'.format(filename)
            )
            msg.attach(part)

        for image in images:
            url = image["url"]
            tag = image["tag"]
            with open(url, "rb") as img:
                msgImage = MIMEImage(img.read())
                msgImage.add_header("Content-ID", "<" + tag + ">")
                msg.attach(msgImage)

        try:
            smtp = smtplib.SMTP(server, port)
            if use_tls:
                smtp.starttls()
            if username != "" and password != "":
                smtp.login(username, password)
            smtp.sendmail(send_from, send_to, msg.as_string())
            smtp.quit()
            respuesta["exito"] = True
        except Exception as e:
            respuesta["mensaje"] = "Mailer Error: " + repr(e)
            respuesta["exito"] = False
            # raise RuntimeError("Mailer Error: " + repr(e))

        return respuesta
