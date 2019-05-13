from app.models.pedido import pedido as pedido_model
from app.models.pedidodireccion import pedidodireccion as pedidodireccion_model
from app.models.pedidoproducto import pedidoproducto as pedidoproducto_model
from app.models.producto import producto as producto_model
from app.models.usuario import usuario as usuario_model
from app.models.seo import seo as seo_model

from core.app import app
from core.functions import functions
from core.image import image

from .base import base

from .head import head
from .header import header
from .banner import banner
from .breadcrumb import breadcrumb
from .footer import footer

import json


class cart(base):
    def __init__(self,):
        super().__init__(app.idseo, False)

    def index(self):
        ret = {"body": []}
        self.meta(self.seo)

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
            self.seo["banner"], self.metadata["title"], self.seo["subtitulo"]
        )["body"]

        f = footer()
        ret["body"] += f.normal()["body"]

        return ret

    @staticmethod
    def current_cart(return_cart: bool = False):
        """ Description
            busca el carro actual, si no existe devuelve un array vacio
            si return_cart es True, retorna array
            si es False, retorna JSON
        :type return_cart:bool:
        :param return_cart:bool:

        :raises:

        :rtype:
        """
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }

        prefix_site = app.prefix_site
        if (
            "cookie_pedido" + prefix_site not in app.session
            or "" == app.session["cookie_pedido" + prefix_site]
        ):
            logueado = usuario_model.verificar_sesion()
            if not logueado:
                cookie = functions.get_cookie("cookieusuario" + prefix_site)
                if cookie != False:
                    logueado = usuario_model.login_cookie(cookie)

            if logueado:
                carro = pedido_model.getByIdusuario(
                    app.session[usuario_model.idname + prefix_site]
                )
                if len(carro) > 0:
                    app.session["cookie_pedido" + prefix_site] = carro["cookie_pedido"]

        if (
            "cookie_pedido" + prefix_site in app.session
            and "" != app.session["cookie_pedido" + prefix_site]
        ):
            carro = cart.get_cart(app.session["cookie_pedido" + prefix_site])
            if len(carro) > 0:
                if return_cart:
                    return carro
                else:
                    ret["body"] = json.dumps(carro, ensure_ascii=False)
                    return ret
        if return_cart:
            return {}
        else:
            ret["body"] = json.dumps({}, ensure_ascii=False)
            return ret

    @staticmethod
    def get_cart(cookie_pedido: str, estado_carro=True):
        """ genera un array que contiene los datos del producto, y dentro un array de productos con datos procesados para ser mostrados.
        :type cookie_pedido:str:
        :param cookie_pedido:str:

        :raises:

        :rtype:
        """

        pedido = pedido_model.getByCookie(cookie_pedido,estado_carro)
        if len(pedido) > 0:
            prod = pedidoproducto_model.getAll({"idpedido": pedido[0]})
            productos = []
            seo_producto = seo_model.getById(8)
            lista = producto_model.getAll({"tipo": 1})
            lista_productos = {}
            for lp in lista:
                lista_productos[lp[0]] = lp

            for p in prod:
                portada = image.portada(p["foto"])
                thumb_url = image.generar_url(portada, "")
                producto = lista_productos[p["idproducto"]]
                url_producto = functions.url_seccion(
                    [seo_producto["url"], "detail"], producto
                )
                new_p = {
                    "idpedidoproducto": p["idpedidoproducto"],
                    "idpedidodireccion": p["idpedidodireccion"],
                    "idproducto": p["idproducto"],
                    "titulo": p["titulo"],
                    "foto": thumb_url,
                    "precio": functions.formato_precio(p["precio"]),
                    "cantidad": p["cantidad"],
                    "mensaje": p["mensaje"],
                    "idproductoatributo": p["idproductoatributo"],
                    "total": functions.formato_precio(p["total"]),
                    "url": url_producto,
                    "stock": producto["stock"] + p["cantidad"],
                }
                productos.append(new_p)

            total_direcciones = 0
            direcciones = pedidodireccion_model.getAll({"idpedido": pedido[0]})
            for d in direcciones:
                total_direcciones += d["precio"]

            subtotal = pedido["total"] - total_direcciones
            if 0 == total_direcciones:
                total_direcciones = "Por definir"
            else:
                total_direcciones = functions.formato_precio(total_direcciones)

            pedido = {
                "idpedido": pedido[0],
                "cookie_pedido": pedido["cookie_pedido"],
                "total": functions.formato_precio(pedido["total"]),
                "total_original": functions.formato_precio(pedido["total_original"]),
                "total_direcciones": total_direcciones,
                "subtotal": functions.formato_precio(subtotal),
                "productos": productos,
            }
            return pedido
        else:
            return {}

    @staticmethod
    def new_cart():
        """ crea un nuevo carro
        :raises:

        :rtype:
        """
        cookie_pedido = functions.generar_pass()
        insert = {
            "tipo": 1,
            "idpedidoestado": 1,
            "fecha_creacion": functions.current_time(),
            "total": 0,
            "total_original": 0,
            "pedido_manual": False,
            "cookie_pedido": cookie_pedido,
        }

        if usuario_model.idname + app.prefix_site in app.session:
            usuario = usuario_model.getById(
                app.session[usuario_model.idname + app.prefix_site]
            )
            if len(usuario) > 0:
                insert["idusuario"] = usuario[0]
                insert["nombre"] = usuario["nombre"]
                insert["email"] = usuario["email"]
                insert["telefono"] = usuario["telefono"]

        idpedido = pedido_model.insert(insert)
        if isinstance(idpedido, int):
            app.session["cookie_pedido" + app.prefix_site] = cookie_pedido
            return cart.get_cart(cookie_pedido)
        else:
            return False

    def add_cart(self):
        """ add_cart
            agrega un producto al carro
            si no existe, crea un carro nuevo
            EN ESTA VERSION, AGREGA PRODUCTOS REPETIDOS CON CANTIDAD 1
            para actualizar elementos en vez de agregar con cantidad 1, se debe descomentar las lineas comentadas
            y desactivar el for que recorre la cantidad, dejando solo una linea para agregar el producto al carro.

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
        campos = app.post
        if "id" not in campos or "cantidad" not in campos:
            respuesta["mensaje"] = "No has agregado un producto valido"
            ret["body"] = json.dumps(respuesta, ensure_ascii=False)
            return ret

        id = int(campos["id"])
        cantidad = int(campos["cantidad"])
        cart = self.current_cart(True)
        if len(cart) == 0:
            cart = self.new_cart()
            if not isinstance(cart, dict):
                respuesta[
                    "mensaje"
                ] = "Hubo un error al crear el carro, por favor intenta nuevamente"
                ret["body"] = json.dumps(respuesta, ensure_ascii=False)
                return ret

        producto = producto_model.getById(id)
        if "precio" not in producto or producto["precio"] <= 0:
            respuesta[
                "mensaje"
            ] = "No se encontro el producto que estas buscando, por favor actualiza la pagina e intenta nuevamente"
            ret["body"] = json.dumps(respuesta, ensure_ascii=False)
            return ret

        cantidad_final = producto["stock"] - cantidad
        if producto["stock"] < 1 or cantidad_final < 0:
            respuesta["mensaje"] = "No hay suficientes productos disponibles"
            ret["body"] = json.dumps(respuesta, ensure_ascii=False)
            return ret

        existe = False

        # foreach (cart['productos'] as key : p:
        # if(p['idproducto']==producto[0])
        # p['cantidad']+=cantidad
        # p['precio']+=producto['precio_final']
        # p['total']=cantidad*p['precio_final']
        # cart['productos'][key]=p
        # p['id']=p['idpedidoproducto']
        # existe=True
        # unset(p['foto'])
        # pedidoproducto_model.update(p)
        # break

        if not existe:
            insert = {
                "idpedido": cart["idpedido"],
                "idproducto": producto[0],
                "titulo": producto["titulo"],
                "precio": producto["precio_final"],
            }

            # insert['cantidad']=cantidad
            # insert['total']=producto['precio']*cantidad
            # idpedidoproducto=pedidoproducto_model.insert(insert)
            # new_p=array()
            # new_p['id'] = idpedidoproducto
            # portada     = image.portada(producto['foto'])
            # copiar      = image.copy(portada, new_p['id'], pedidoproducto_model.table, '', '', 'cart'}
            # if copiar['exito']:
            # new_p['foto']    = json_encode(copiar['file'])
            # idpedidoproducto = pedidoproducto_model.update(new_p)

            # comentar esto para funcionamiento tipico de actualizar cantidades en lugar de agregar siempre algo nuevo
            for i in range(cantidad):
                insert["cantidad"] = 1
                insert["total"] = producto["precio_final"] * 1
                idpedidoproducto = pedidoproducto_model.insert(insert)
                new_p = {}
                new_p["id"] = idpedidoproducto
                portada = image.portada(producto["foto"])
                copiar = image.copy(
                    portada, new_p["id"], pedidoproducto_model.table, "", "", "cart"
                )
                if copiar["exito"]:
                    new_p["foto"] = json.dumps(copiar["file"])
                    idpedidoproducto = pedidoproducto_model.update(new_p)

            # comentar esto para funcionamiento tipico de actualizar cantidades en lugar de agregar siempre algo nuevo

        self.update_cart(cart["idpedido"])

        actualizar_producto = {"id": producto[0], "stock": cantidad_final}
        producto_model.update(actualizar_producto)
        respuesta["carro"] = self.current_cart(True)
        respuesta["mensaje"] = (
            producto["titulo"]
            + ' agregado al carro.<br/> <i class="fa fa-shopping-bag"></i> Puedes Comprar haciendo click aqui'
        )
        respuesta["exito"] = True
        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    @staticmethod
    def remove_cart():
        """ quita un producto del carro
        :raises:

        :rtype:
        """
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {"exito": False, "mensaje": ""}
        producto = None
        campos = app.post
        if "id" not in campos:
            respuesta["mensaje"] = "No has agregado un producto valido"
            ret["body"] = json.dumps(respuesta, ensure_ascii=False)
            return ret

        id = int(campos["id"])
        carro = cart.current_cart(True)
        if len(carro) == 0:
            carro = cart.new_cart()
            if not isinstance(carro, dict):
                respuesta[
                    "mensaje"
                ] = "Hubo un error al eliminar del carro, por favor actualiza la pagina e intenta nuevamente"
                ret["body"] = json.dumps(respuesta, ensure_ascii=False)
                return ret

        cantidad = 0
        for p in carro["productos"]:
            if p["idpedidoproducto"] == id:
                cantidad = p["cantidad"]
                producto = producto_model.getById(p["idproducto"])
                if "precio" not in producto or producto["precio"] <= 0:
                    respuesta[
                        "mensaje"
                    ] = "No se encontro el producto que estas buscando, por favor actualiza la pagina e intenta nuevamente"
                    ret["body"] = json.dumps(respuesta, ensure_ascii=False)
                    return ret

                pedidoproducto_model.delete(p["idpedidoproducto"])
                break

        cart.update_cart(carro["idpedido"])
        producto_titulo = ""

        if producto != None:
            cantidad_final = producto["stock"] + cantidad
            actualizar_producto = {"id": producto[0], "stock": cantidad_final}
            producto_model.update(actualizar_producto)
            producto_titulo = producto["titulo"]

        respuesta["carro"] = cart.current_cart(True)
        respuesta["mensaje"] = producto_titulo + " eliminado del carro"
        respuesta["exito"] = True
        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    @staticmethod
    def update_cart(idpedido: int):
        """ Actualiza la informacion del pedido, segun un id de pedido enviado
        :type idpedido:int:
        :param idpedido:int:

        :raises:

        :rtype:
        """

        pedido = pedido_model.getById(idpedido)
        total = 0
        productos = pedidoproducto_model.getAll({"idpedido": pedido[0]})
        for p in productos:
            total += p["total"]

        direcciones = pedidodireccion_model.getAll({"idpedido": pedido[0]})
        for d in direcciones:
            total += d["precio"]

        update = {"total": total, "total_original": total}
        if usuario_model.idname + app.prefix_site in app.session:
            usuario = usuario_model.getById(
                app.session[usuario_model.idname + app.prefix_site]
            )
            if len(usuario) > 0:
                update["idusuario"] = usuario[0]
                update["nombre"] = usuario["nombre"]
                update["email"] = usuario["email"]
                update["telefono"] = usuario["telefono"]

        update["id"] = pedido[0]
        pedido_model.update(update)

    @staticmethod
    def change_atributo():
        """ cambia el atributo en el producto correspondiente al pedido actual
            si el producto no corresponde al pedido, lanza error
        :type id:int: POST
        :param id:int: POST

        :type cantidad:int: POST
        :param cantidad:int: POST

        :raises:

        :rtype: json
        """
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {
            "exito": False,
            "mensaje": "No has modificado un producto valido. Por favor recarga la pagina e intenta nuevamente",
        }
        campos = app.post
        if "idproductoatributo" in campos and "idpedidoproducto" in campos:
            carro = cart.current_cart(True)
            if "productos" in carro:
                for p in carro["productos"]:
                    if p["idpedidoproducto"] == int(campos["idpedidoproducto"]):
                        atributo = producto_model.getById(
                            int(campos["idproductoatributo"])
                        )
                        update = {
                            "id": p["idpedidoproducto"],
                            "idproductoatributo": int(campos["idproductoatributo"]),
                            "titulo_atributo": atributo["titulo"],
                        }
                        idpedidoproducto = pedidoproducto_model.update(update)
                        respuesta["exito"] = True
                        break

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    @staticmethod
    def change_mensaje():
        """ cambia el mensaje en el producto correspondiente al pedido actual
            si el producto no corresponde al pedido, lanza error

        :type id:int: POST
        :param id:int: POST

        :type cantidad:int: POST
        :param cantidad:int: POST

        :raises:

        :rtype: json
        """
        ret = {
            "headers": [("Content-Type", "application/json; charset=utf-8")],
            "body": "",
        }
        respuesta = {
            "exito": False,
            "mensaje": "No has modificado un producto valido. Por favor recarga la pagina e intenta nuevamente",
        }
        campos = app.post
        if "mensaje" in campos and "idpedidoproducto" in campos:
            carro = cart.current_cart(True)
            if "productos" in carro:
                for p in carro["productos"]:
                    if p["idpedidoproducto"] == int(campos["idpedidoproducto"]):
                        update = {
                            "id": p["idpedidoproducto"],
                            "mensaje": campos["mensaje"],
                        }
                        pedidoproducto_model.update(update)
                        respuesta["exito"] = True
                        break

        ret["body"] = json.dumps(respuesta, ensure_ascii=False)
        return ret
