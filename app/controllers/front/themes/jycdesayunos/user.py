from app.models.mediopago import mediopago as mediopago_model
from app.models.modulo import modulo as modulo_model
from app.models.moduloconfiguracion import (
    moduloconfiguracion as moduloconfiguracion_model,
)
from app.models.comuna import comuna as comuna_model
from app.models.usuario import usuario as usuario_model
from app.models.usuariodireccion import usuariodireccion as usuariodireccion_model
from app.models.pedido import pedido as pedido_model
from app.models.pedidodireccion import pedidodireccion as pedidodireccion_model
from app.models.pedidoestado import pedidoestado as pedidoestado_model
from app.models.pedidoproducto import pedidoproducto as pedidoproducto_model
from app.models.seo import seo as seo_model

from .base import base


from .head import head
from .header import header
from .banner import banner
from .breadcrumb import breadcrumb
from .footer import footer

from core.app import app
from core.image import image
from core.functions import functions

import json


class user(base):
    def __init__(self):
        super().__init__(app.idseo, False)

    def index(self):
        ret = {"body": []}
        self.meta(self.seo)
        verificar = self.verificar(True)
        if not verificar["exito"]:
            self.url.append("login")

        url_return = functions.url_redirect(self.url)
        if url_return != "":
            ret["error"] = 301
            ret["redirect"] = url_return
            return ret

        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        he = header()
        ret["body"] += he.normal()["body"]

        ba = banner()
        ret["body"] += ba.individual(self.seo["banner"], self.metadata["title"])["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        sidebar = []
        sidebar.append(
            {
                "title": "Mis datos",
                "active": "",
                "url": functions.generar_url([self.url[0], "datos"]),
            }
        )
        sidebar.append(
            {
                "title": "Mis direcciones",
                "active": "",
                "url": functions.generar_url([self.url[0], "direcciones"]),
            }
        )
        sidebar.append(
            {
                "title": "Mis pedidos",
                "active": "",
                "url": functions.generar_url([self.url[0], "pedidos"]),
            }
        )

        data = {}
        data["sidebar"] = ("user/sidebar", {"sidebar_user": sidebar})
        ret["body"].append(("user/detail", data))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

    def datos(self):
        from time import time

        ret = {"body": []}
        self.meta(self.seo)
        verificar = self.verificar(True)
        if verificar["exito"]:
            self.url.append("datos")
        else:
            self.url.append("login")

        url_return = functions.url_redirect(self.url)
        if url_return != "":
            ret["error"] = 301
            ret["redirect"] = url_return
            return ret

        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        he = header()
        ret["body"] += he.normal()["body"]

        ba = banner()
        ret["body"] += ba.individual(
            self.seo["banner"], self.metadata["title"], "Mis datos"
        )["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        sidebar = []
        sidebar.append(
            {
                "title": "Mis datos",
                "active": "active",
                "url": functions.generar_url([self.url[0], "datos"]),
            }
        )
        sidebar.append(
            {
                "title": "Mis direcciones",
                "active": "",
                "url": functions.generar_url([self.url[0], "direcciones"]),
            }
        )
        sidebar.append(
            {
                "title": "Mis pedidos",
                "active": "",
                "url": functions.generar_url([self.url[0], "pedidos"]),
            }
        )

        data = {}
        data["sidebar"] = ("user/sidebar", {"sidebar_user": sidebar})

        usuario = usuario_model.getById(
            app.session[usuario_model.idname + app.prefix_site]
        )
        data["nombre"] = usuario["nombre"]
        data["telefono"] = usuario["telefono"]
        data["email"] = usuario["email"]
        token = functions.generar_pass(20)
        app.session["datos_token"] = {"token": token, "time": time()}
        data["token"] = token
        ret["body"].append(("user/datos", data.copy()))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

    def datos_process(self):
        from time import time

        """ procesa el POST para modificacion de datos
        :type self:
        :param self:
    
        :raises:
    
        :rtype: json
        """
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }

        respuesta = {"exito": False, "mensaje": ""}
        verificar = self.verificar(True)
        if not verificar["exito"]:
            respuesta["mensaje"] = "Debes ingresar a tu cuenta"
            ret["body"] = json.dumps(respuesta, ensure_ascii=False)
            return ret

        campos = app.post["campos"]

        if (
            "nombre" in campos
            and "telefono" in campos
            and "email" in campos
            and "token" in campos
        ):
            if (
                "token" in app.session["datos_token"]
                and app.session["datos_token"]["token"] == campos["token"]
            ):
                if time() - app.session["datos_token"]["time"] <= 120:
                    datos = {
                        "nombre": campos["nombre"],
                        "telefono": campos["telefono"],
                        "email": campos["email"],
                        "pass": campos["pass"]
                        if "pass" in campos and campos["pass"] != ""
                        else "",
                        "pass_repetir": campos["pass_repetir"]
                        if "pass_repetir" in campos and campos["pass_repetir"] != ""
                        else "",
                    }
                    respuesta = usuario_model.actualizar(datos)
                    if respuesta["exito"]:
                        respuesta["mensaje"] = "Datos modificados correctamente"
                else:
                    respuesta[
                        "mensaje"
                    ] = "Error de token, recarga la pagina e intenta nuevamente"
            else:
                respuesta[
                    "mensaje"
                ] = "Error de token, recarga la pagina e intenta nuevamente"
        else:
            respuesta["mensaje"] = "Debes llenar los campos obligatorios"

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    def direcciones(self):
        """ lista de direcciones
        :type self:
        :param self:
    
        :raises:
    
        :rtype:
        """
        ret = {"body": []}
        self.meta(self.seo)
        verificar = self.verificar(True)
        if verificar["exito"]:
            self.url.append("direcciones")
        else:
            self.url.append("login")

        url_return = functions.url_redirect(self.url)
        if url_return != "":
            ret["error"] = 301
            ret["redirect"] = url_return
            return ret

        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        he = header()
        ret["body"] += he.normal()["body"]

        ba = banner()
        ret["body"] += ba.individual(
            self.seo["banner"], self.metadata["title"], "Mis direcciones"
        )["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        sidebar = []
        sidebar.append(
            {
                "title": "Mis datos",
                "active": "",
                "url": functions.generar_url([self.url[0], "datos"]),
            }
        )
        sidebar.append(
            {
                "title": "Mis direcciones",
                "active": "active",
                "url": functions.generar_url([self.url[0], "direcciones"]),
            }
        )
        sidebar.append(
            {
                "title": "Mis pedidos",
                "active": "",
                "url": functions.generar_url([self.url[0], "pedidos"]),
            }
        )

        data = {}
        data["sidebar"] = ("user/sidebar", {"sidebar_user": sidebar})

        dir = usuariodireccion_model.getAll(
            {"idusuario": app.session[usuario_model.idname + app.prefix_site]}
        )
        direcciones = []
        for d in dir:
            direcciones.append(
                {
                    "title": d["titulo"],
                    "nombre": d["nombre"],
                    "direccion": d["direccion"],
                    "telefono": d["telefono"],
                    "url": functions.generar_url([self.url[0], "direccion", d[0]]),
                }
            )

        data["direcciones"] = direcciones
        data["url_new"] = functions.generar_url([self.url[0], "direccion"])
        ret["body"].append(("user/direcciones-lista", data))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

    def direccion(self, var=[]):
        """ modificar o crear direccion
        :type var:
        :param var:
    
        :raises:
    
        :rtype:
        """
        from time import time

        ret = {"body": []}
        direccion = None
        self.meta(self.seo)
        verificar = self.verificar(True)
        if verificar["exito"]:
            if len(var) > 0:
                direccion = usuariodireccion_model.getById(var[0])
                if (
                    direccion["idusuario"]
                    == app.session[usuario_model.idname + app.prefix_site]
                ):
                    self.url.append("direccion")
                    self.url.append(var[0])
                else:
                    self.url.append("direcciones")
            else:
                self.url.append("direccion")
        else:
            self.url.append("login")

        url_return = functions.url_redirect(self.url)
        if url_return != "":
            ret["error"] = 301
            ret["redirect"] = url_return
            return ret

        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        he = header()
        ret["body"] += he.normal()["body"]

        ba = banner()
        ret["body"] += ba.individual(
            self.seo["banner"], self.metadata["title"], "Modificar dirección"
        )["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        sidebar = []
        sidebar.append(
            {
                "title": "Mis datos",
                "active": "",
                "url": functions.generar_url([self.url[0], "datos"]),
            }
        )
        sidebar.append(
            {
                "title": "Mis direcciones",
                "active": "active",
                "url": functions.generar_url([self.url[0], "direcciones"]),
            }
        )
        sidebar.append(
            {
                "title": "Mis pedidos",
                "active": "",
                "url": functions.generar_url([self.url[0], "pedidos"]),
            }
        )

        data = {}
        data["sidebar"] = ("user/sidebar", {"sidebar_user": sidebar})

        moduloconfiguracion = moduloconfiguracion_model.getByModulo("usuariodireccion")
        if 0 in moduloconfiguracion:
            modulo = modulo_model.getAll(
                {"idmoduloconfiguracion": moduloconfiguracion[0], "tipo": 1}
            )
            modulo = modulo[0]["detalle"]
        else:
            modulo = []

        com = comuna_model.getAll({}, {"order": "titulo ASC"})
        comunas = []
        for c in com:
            comunas.append(
                {
                    "title": c["titulo"],
                    "value": c[0],
                    "selected": (direccion != None and direccion["idcomuna"] == c[0]),
                }
            )

        campos_requeridos = []
        campos_opcionales = []
        for m in modulo:
            if True in m["estado"].values() or 'true' in m["estado"].values():
                del m["estado"]
                if m["field"] == "idcomuna":
                    m["options"] = comunas
                else:
                    m["value"] = direccion[m["field"]] if direccion != None else ""

                if m["required"]:
                    campos_requeridos.append(m)
                else:
                    campos_opcionales.append(m)

        data["campos_requeridos"] = campos_requeridos
        data["campos_opcionales"] = campos_opcionales
        data["title"] = direccion["titulo"] if direccion != None else "Nueva dirección"
        data["id"] = direccion[0] if direccion != None else ""

        token = functions.generar_pass(20)
        app.session["direccion_token"] = {"token": token, "time": time()}
        data["token"] = token

        ret["body"].append(("user/direcciones-detalle", data))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

    def direccion_process(self):
        """ procesa el POST para modificacion de direccion
        :type self:
        :param self:
    
        :raises:
    
        :rtype: json
        """
        from time import time

        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }

        respuesta = {"exito": False, "mensaje": ""}

        verificar = self.verificar(True)
        if not verificar["exito"]:
            respuesta["mensaje"] = "Debes ingresar a tu cuenta"
            ret["body"] = json.dumps(respuesta, ensure_ascii=False)
            return ret
        campos = app.post["campos"]

        if "token" in campos and "id" in campos:
            if (
                "token" in app.session["direccion_token"]
                and app.session["direccion_token"]["token"] == campos["token"]
            ):
                if time() - app.session["direccion_token"]["time"] <= 360:
                    del campos["token"]
                    campos["idusuario"] = app.session[
                        usuario_model.idname + app.prefix_site
                    ]
                    campos["tipo"] = 1
                    if campos["id"] != "":
                        respuesta["exito"] = usuariodireccion_model.update(campos)
                    else:
                        respuesta["exito"] = usuariodireccion_model.insert(campos)

                    if respuesta["exito"]:
                        respuesta["mensaje"] = "Direccion guardada correctamente"

                        if "next_url" in app.get:
                            respuesta["next_url"] = app.get["next_url"]

                    else:
                        respuesta[
                            "mensaje"
                        ] = "Hubo un error al guardar la direccion, comprueba los campos obligatorios e intentalo nuevamente"

                else:
                    respuesta[
                        "mensaje"
                    ] = "Error de token, recarga la pagina e intenta nuevamente"

            else:
                respuesta[
                    "mensaje"
                ] = "Error de token, recarga la pagina e intenta nuevamente"

        else:
            respuesta["mensaje"] = "Debes llenar los campos obligatorios"

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    def pedidos(self):
        """ lista de pedidos
        :type self:
        :param self:
    
        :raises:
    
        :rtype:
        """
        ret = {"body": []}
        self.meta(self.seo)
        verificar = self.verificar(True)
        if verificar["exito"]:
            self.url.append("pedidos")
        else:
            self.url.append("login")

        url_return = functions.url_redirect(self.url)
        if url_return != "":
            ret["error"] = 301
            ret["redirect"] = url_return
            return ret

        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        he = header()
        ret["body"] += he.normal()["body"]

        ba = banner()
        ret["body"] += ba.individual(
            self.seo["banner"], self.metadata["title"], "Mis Pedidos"
        )["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        sidebar = []
        sidebar.append(
            {
                "title": "Mis datos",
                "active": "",
                "url": functions.generar_url([self.url[0], "datos"]),
            }
        )
        sidebar.append(
            {
                "title": "Mis direcciones",
                "active": "",
                "url": functions.generar_url([self.url[0], "direcciones"]),
            }
        )
        sidebar.append(
            {
                "title": "Mis pedidos",
                "active": "active",
                "url": functions.generar_url([self.url[0], "pedidos"]),
            }
        )

        data = {}
        data["sidebar"] = ("user/sidebar", {"sidebar_user": sidebar})

        ep = pedidoestado_model.getAll({"tipo": 1})
        estados_pedido = {}
        for e in ep:
            estados_pedido[e[0]] = e

        usuario = usuario_model.getById(
            app.session[usuario_model.idname + app.prefix_site]
        )
        pedidos = pedido_model.getByIdusuario(
            usuario[0], False
        )  # obtiene todos los pedidos del usuario actual, con cualquier estado del pedido
        pedidos_lista=[]
        for p in pedidos:
            if p["idpedidoestado"] != 1:  # Quita cualquier pedido que este en carro
                p["total"] = functions.formato_precio(p["total"])
                p["fecha"] = (
                    p["fecha_pago"] if p["fecha_pago"] != '0000-00-00 00:00:00' else p["fecha_creacion"]
                )
                p["fecha"]=functions.formato_fecha(p['fecha'],'%d de %B del %Y a las %H:%M')
                p["url"] = functions.generar_url(
                    [self.url[0], "pedido", p["cookie_pedido"]]
                )
                p["estado"] = estados_pedido[p["idpedidoestado"]]["titulo"]
                p["background_estado"] = estados_pedido[p["idpedidoestado"]]["color"]
                p["color_estado"] = functions.getContrastColor(
                    estados_pedido[p["idpedidoestado"]]["color"]
                )
                pedidos_lista.append(p)

        data["pedidos"] = pedidos_lista
        ret["body"].append(("user/pedidos-lista", data))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

    def pedido(self, var=[]):
        """ Ver o pagar pedido
        :param var:
    
        :raises:
    
        :rtype:
        """
        ret = {"body": []}
        self.meta(self.seo)
        verificar = self.verificar(True)
        if verificar["exito"]:
            if len(var) > 0:
                pedido = pedido_model.getByCookie(var[0], False)
                # Podria desaparecer si se necesita que cualquier pedido sea publico
                if ( "idusuario" in pedido and pedido["idusuario"] == app.session[usuario_model.idname + app.prefix_site] ):
                    self.url.append("pedido")
                    self.url.append(var[0])
                else:
                    # Podria desaparecer si se necesita que cualquier pedido sea publico
                    self.url.append("pedidos")
            else:
                self.url.append("pedido")

        else:
            self.url.append("login")

        url_return = functions.url_redirect(self.url)
        if url_return != "":
            ret["error"] = 301
            ret["redirect"] = url_return
            return ret

        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        he = header()
        ret["body"] += he.normal()["body"]

        ba = banner()
        ret["body"] += ba.individual(
            self.seo["banner"], self.metadata["title"], "Detalle del pedido"
        )["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        sidebar = []
        sidebar.append(
            {
                "title": "Mis datos",
                "active": "",
                "url": functions.generar_url([self.url[0], "datos"]),
            }
        )
        sidebar.append(
            {
                "title": "Mis direcciones",
                "active": "",
                "url": functions.generar_url([self.url[0], "direcciones"]),
            }
        )
        sidebar.append(
            {
                "title": "Mis pedidos",
                "active": "active",
                "url": functions.generar_url([self.url[0], "pedidos"]),
            }
        )

        data = {}
        data["sidebar"] = ("user/sidebar", {"sidebar_user": sidebar})

        ep = pedidoestado_model.getAll()
        estados_pedido = {}
        for e in ep:
            estados_pedido[e[0]] = e

        direcciones_pedido = pedidodireccion_model.getAll(
            {"idpedido": pedido["idpedido"]}
        )
        productos_pedido = pedidoproducto_model.getAll({"idpedido": pedido["idpedido"]})
        for dp in direcciones_pedido:
            dp["precio"] = functions.formato_precio(dp["precio"])
            dp["estado"] = estados_pedido[dp["idpedidoestado"]]["titulo"]
            dp["background_estado"] = estados_pedido[dp["idpedidoestado"]]["color"]
            dp["color_estado"] = functions.getContrastColor(
                estados_pedido[dp["idpedidoestado"]]["color"]
            )
            dp["fecha_entrega"]=functions.formato_fecha(dp['fecha_entrega'],'%d de %B del %Y a las %H:%M')
            lista_productos = []
            productos_pedido_copy=[]
            for p in productos_pedido:
                if p["idpedidodireccion"] == dp[0]:
                    portada = image.portada(p["foto"])
                    thumb_url = image.generar_url(portada, "")
                    p["total"] = functions.formato_precio(p["total"])
                    p["foto"] = thumb_url
                    lista_productos.append(p)
                else:
                    productos_pedido_copy.append(p)
            productos_pedido=productos_pedido_copy
                    
            
            dp['lista_productos']=lista_productos

        pedido["total"] = functions.formato_precio(pedido["total"])
        pedido["direcciones_pedido"] = direcciones_pedido
        pedido["estado"] = estados_pedido[pedido["idpedidoestado"]]["titulo"]
        pedido["background_estado"] = estados_pedido[pedido["idpedidoestado"]]["color"]
        pedido["color_estado"] = functions.getContrastColor(
            estados_pedido[pedido["idpedidoestado"]]["color"]
        )



        medios_pago = []
        descripcion_pago = ""
        if (
            pedido["idpedidoestado"] == 3 or pedido["idpedidoestado"] == 7
        ):  # Solo si hay pago pendiente
            medios_pago = mediopago_model.getAll()
            seo_pago = seo_model.getById(12)  # seo medios de pago
            for mp in medios_pago:
                mp["url"] = functions.generar_url(
                    [seo_pago["url"], "medio", mp[0], pedido["cookie_pedido"]]
                )
        else:
            medio_pago = mediopago_model.getById(pedido["idmediopago"])
            descripcion_pago = medio_pago["descripcion"]

        pedido = {k:p for (k,p) in pedido.items() if isinstance(k,str)}
        data.update(pedido)
        data["medios_pago"] = medios_pago
        data["descripcion_pago"] = descripcion_pago
        data["is_descripcion_pago"] = (
            functions.remove_tags(descripcion_pago)
        ).strip() != ""

        ret["body"].append(("user/pedidos-detalle", data))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

    def registro(self):
        from time import time

        ret = {"body": []}
        self.meta(self.seo)

        verificar = self.verificar(True)
        if verificar["exito"]:
            if "next_url" in app.get:
                self.url = app.get["next_url"].split("/")
            else:
                self.url.append("datos")

        else:
            self.url.append("registro")

        url_return = functions.url_redirect(self.url)
        if url_return != "":
            ret["error"] = 301
            ret["redirect"] = url_return
            return ret

        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        he = header()
        ret["body"] += he.normal()["body"]

        ba = banner()
        ret["body"] += ba.individual(self.seo["banner"], "Registro")["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        token = functions.generar_pass(20)
        app.session["registro_token"] = {"token": token, "time": time()}
        data = {}
        data["token"] = token
        data["url_login"] = functions.generar_url([self.url[0], "login"])

        ret["body"].append(("user/registro", data))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

    def registro_process(self):
        """ procesa el POST para registro
        :param self:
    
        :raises:
    
        :rtype: json
        """
        from time import time

        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {"exito": False, "mensaje": ""}
        campos = app.post["campos"]

        if (
            "nombre" in campos
            and "telefono" in campos
            and "email" in campos
            and "pass" in campos
            and "pass_repetir" in campos
            and "token" in campos
        ):
            if (
                "token" in app.session["registro_token"]
                and app.session["registro_token"]["token"] == campos["token"]
            ):
                if time() - app.session["registro_token"]["time"] <= 120:
                    respuesta = usuario_model.registro(
                        campos["nombre"],
                        campos["telefono"],
                        campos["email"],
                        campos["pass"],
                        campos["pass_repetir"],
                    )
                    if respuesta["exito"]:
                        respuesta["exito"] = usuario_model.login(
                            campos["email"], campos["pass"], isset(campos["recordar"])
                        )
                        if not respuesta["exito"]:
                            respuesta[
                                "mensaje"
                            ] = "Cuenta creada correctamente, pero ha ocurrido un error al ingresar. Intenta loguearte"
                        else:
                            respuesta["mensaje"] = "Bienvenido"
                else:
                    respuesta[
                        "mensaje"
                    ] = "Error de token, recarga la pagina e intenta nuevamente"
            else:
                respuesta[
                    "mensaje"
                ] = "Error de token, recarga la pagina e intenta nuevamente"
        else:
            respuesta["mensaje"] = "Debes llenar todos los campos"

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    def recuperar(self):
        from time import time

        ret = {"body": []}
        self.meta(self.seo)
        self.url.append("recuperar")

        url_return = functions.url_redirect(self.url)
        if url_return != "":
            ret["error"] = 301
            ret["redirect"] = url_return
            return ret

        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        he = header()
        ret["body"] += he.normal()["body"]

        ba = banner()
        ret["body"] += ba.individual(self.seo["banner"], "Recuperar contraseña")["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        token = functions.generar_pass(20)
        app.session["recuperar_token"] = {"token": token, "time": time()}
        data = {}
        data["token"] = token
        data["url_registro"] = functions.generar_url([self.url[0], "registro"])

        ret["body"].append(("user/recuperar", data))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

    def recuperar_process(self):

        """ procesa el POST para recuperacion de contraseña
        :param self:
    
        :raises:
    
        :rtype: json
        """
        from time import time

        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {"exito": False, "mensaje": ""}
        campos = app.post["campos"]

        if "email" in campos and "token" in campos:
            if (
                "token" in app.session["recuperar_token"]
                and app.session["recuperar_token"]["token"] == campos["token"]
            ):
                if time() - app.session["recuperar_token"]["time"] <= 120:
                    respuesta = usuario_model.recuperar(campos["email"])
                    if respuesta["exito"]:
                        respuesta[
                            "mensaje"
                        ] = "Se ha enviado tu nueva contraseña a tu email. recuerda modificarla al ingresar."
                else:
                    respuesta[
                        "mensaje"
                    ] = "Error de token, recarga la pagina e intenta nuevamente"
            else:
                respuesta[
                    "mensaje"
                ] = "Error de token, recarga la pagina e intenta nuevamente"
        else:
            respuesta["mensaje"] = "Debes llenar todos los campos"

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    def login(self):
        from time import time

        ret = {"body": []}
        self.meta(self.seo)
        verificar = self.verificar(True)
        if verificar["exito"]:
            if "next_url" in app.get:
                self.url = explode("/", app.get["next_url"])
            else:
                self.url.append("datos")
        else:
            self.url.append("login")

        url_return = functions.url_redirect(self.url)
        if url_return != "":
            ret["error"] = 301
            ret["redirect"] = url_return
            return ret

        h = head(self.metadata)
        ret_head = h.normal()
        if ret_head["headers"] != "":
            return ret_head
        ret["body"] += ret_head["body"]

        he = header()
        ret["body"] += he.normal()["body"]

        ba = banner()
        ret["body"] += ba.individual(self.seo["banner"], "Login")["body"]

        bc = breadcrumb()
        ret["body"] += bc.normal(self.breadcrumb)["body"]

        token = functions.generar_pass(20)
        app.session["login_token"] = {"token": token, "time": time()}
        data = {}
        data["token"] = token
        data["url_recuperar"] = functions.generar_url([self.url[0], "recuperar"])
        data["url_registro"] = functions.generar_url([self.url[0], "registro"])

        ret["body"].append(("user/login", data))

        f = footer()
        ret["body"] += f.normal()["body"]
        return ret

    def login_process(self):

        """ procesa el POST para login
        :param self:
    
        :raises:
    
        :rtype: json
        """
        from time import time

        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {"exito": False, "mensaje": ""}
        campos = app.post["campos"]

        if "email" in campos and "pass" in campos and "token" in campos:
            if (
                "token" in app.session["login_token"]
                and app.session["login_token"]["token"] == campos["token"]
            ):
                if time() - app.session["login_token"]["time"] <= 120:
                    respuesta["exito"] = usuario_model.login(
                        campos["email"], campos["pass"], ("recordar" in campos)
                    )
                    if not respuesta["exito"]:
                        respuesta[
                            "mensaje"
                        ] = "Ha ocurrido un error al ingresar. Revisa tus datos e intenta nuevamente"
                    else:
                        respuesta["mensaje"] = "Bienvenido"
                        if "next_url" in app.get:
                            respuesta["next_url"] = app.get["next_url"]
                else:
                    respuesta["mensaje"] = (
                        "Error de token, recarga la pagina e intenta nuevamente"
                        + (time() - app.session["login_token"]["time"])
                    )
            else:
                respuesta[
                    "mensaje"
                ] = "Error de token, recarga la pagina e intenta nuevamente"
        else:
            respuesta["mensaje"] = "Debes llenar todos los campos"

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    @staticmethod
    def verificar(return_response=False):
        """ Description
        :param return_response:
    
        :raises:
    
        :rtype:dict or json
        """
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {"exito": False, "mensaje": ""}
        logueado = usuario_model.verificar_sesion()
        if not logueado:
            cookie = functions.get_cookie("cookieusuario" + app.prefix_site)
            if cookie != False:
                logueado = usuario_model.login_cookie(cookie)

        respuesta["exito"] = logueado
        if logueado:
            nombre = app.session["nombreusuario" + app.prefix_site].split(" ")[0]
            respuesta["mensaje"] = nombre

        if return_response:
            return respuesta
        else:
            ret["body"] = json.dumps(respuesta, ensure_ascii=False)
            return ret

    def logout(self):
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        usuario_model.logout()
        ret["body"] = json.dumps(
            {"exito": True, "mensaje": "Gracias por visitar nuestro sitio"},
            ensure_ascii=False,
        )
        return ret

