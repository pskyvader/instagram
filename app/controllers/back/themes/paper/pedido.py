from .base import base
from app.models.pedido import pedido as pedido_model

from app.models.table import table as table_model
from app.models.administrador import administrador as administrador_model
#from app.models.modulo import modulo as modulo_model
#from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model

from app.models.comuna import comuna as comuna_model
from app.models.mediopago import mediopago as mediopago_model
from app.models.pedidoestado import pedidoestado as pedidoestado_model
from app.models.pedidodireccion import pedidodireccion as pedidodireccion_model
from app.models.pedidoproducto import pedidoproducto as pedidoproducto_model
from app.models.producto import producto as producto_model
from app.models.region import region as region_model
from app.models.usuario import usuario as usuario_model
from app.models.usuariodireccion import usuariodireccion as usuariodireccion_model


from .detalle import detalle as detalle_class
from .lista import lista as lista_class
#from .head import head
#from .header import header
#from .aside import aside
#from .footer import footer

from core.app import app
from core.database import database
from core.functions import functions
from core.image import image


import json


class pedido(base):
    url = ['pedido']
    metadata = {'title': 'pedido', 'modulo': 'pedido'}
    breadcrumb = []

    def __init__(self):
        super().__init__(pedido_model)

    @classmethod
    def index(cls):
        '''Controlador de lista_class de elementos base, puede ser sobreescrito en el controlador de cada modulo'''
        ret = {'body': ''}
        # Clase para enviar a controlador de lista_class
        class_name = cls.class_name
        url_final = cls.url.copy()
        get = app.get
        if cls.contiene_tipos and not 'tipo' in get:
            url_final = ['home']
        if cls.contiene_hijos and not 'idpadre' in get:
            url_final = ['home']

        if not administrador_model.verificar_sesion():
            url_final = ['login', 'index'] + url_final
        # verificar sesion o redireccionar a login
        url_return = functions.url_redirect(url_final)
        if url_return != '':
            ret['error'] = 301
            ret['redirect'] = url_return
            return ret

        # cabeceras y campos que se muestran en la lista_class:
        # titulo,campo de la tabla a usar, tipo (ver archivo lista_class.py funcion "field")
        # controlador de lista_class
        lista = lista_class(cls.metadata)
        
        configuracion = lista.configuracion(cls.metadata['modulo'])
        if 'error' in configuracion:
            ret['error'] = configuracion['error']
            ret['redirect'] = configuracion['redirect']
            return ret

        head=lista.head()
        if head!=False:
            return head

        where = {}
        if cls.contiene_tipos:
            where['tipo'] = get['tipo']
        if cls.contiene_hijos:
            where['idpadre'] = get['idpadre']
        if cls.class_parent != None:
            class_parent = cls.class_parent
            if class_parent.idname in get:
                where[class_parent.idname] = get[class_parent.idname]

        if 'idpedidoestado' in get and int(get['idpedidoestado']) != 0:
            where['idpedidoestado'] = get['idpedidoestado']

        condiciones = {'order': 'fecha_pago DESC,fecha_creacion DESC'}
        url_detalle = url_final.copy()
        url_detalle.append('detail')
        # obtener unicamente elementos de la pagina actual
        respuesta = lista.get_row(class_name, where, condiciones, url_detalle)

        if 'copy' in configuracion['th']:
            configuracion['th']['copy']['action'] = configuracion['th']['copy']['field']
            configuracion['th']['copy']['field'] = 0
            configuracion['th']['copy']['mensaje'] = 'Copiando'

        if 'idpedidoestado' in configuracion['th']:
            pe = pedidoestado_model.getAll()
            pedidoestado = {}
            for p in pe:
                pedidoestado[p[0]] = {
                    'background': p['color'], 'text': p['titulo'], 'color': functions.getContrastColor(p['color'])}

            for v in respuesta['row']:
                v['idpedidoestado'] = pedidoestado[v['idpedidoestado']]

        if cls.contiene_hijos:
            if cls.contiene_tipos:
                for v in respuesta['row']:
                    v['url_children'] = functions.generar_url(
                        url_final, {'idpadre': v[0], 'tipo': get['tipo']})

            else:
                for v in respuesta['row']:
                    v['url_children'] = functions.generar_url(
                        url_final, {'idpadre': v[0]})

        else:
            if 'url_children' in configuracion['th']:
                del configuracion['th']['url_children']

        if cls.sub != '':
            if cls.contiene_tipos:
                for v in respuesta['row']:
                    v['url_sub'] = functions.generar_url(
                        [cls.sub], {class_name.idname: v[0], 'tipo': get['tipo']})

            else:
                for v in respuesta['row']:
                    v['url_sub'] = functions.generar_url(
                        [cls.sub], {class_name.idname: v[0]})

        else:
            if 'url_sub' in configuracion['th']:
                del configuracion['th']['url_sub']

        # informacion para generar la vista de lista_class
        data = {
            'breadcrumb': cls.breadcrumb,
            'th': configuracion['th'],
            'current_url': functions.generar_url(url_final),
            'new_url': functions.generar_url(url_detalle),
        }

        data.update(respuesta)
        data.update(configuracion['menu'])
        ret = lista.normal(data)
        return ret

    @classmethod
    def detail(cls, var=[]):
        '''Controlador de detalle de elementos base, puede ser sobreescrito en el controlador de cada modulo'''
        ret = {'body': ''}
        # Clase para enviar a controlador de detalle
        class_name = cls.class_name
        get = app.get
        url_list = cls.url.copy()
        url_save = cls.url.copy()
        url_final = cls.url.copy()
        metadata = cls.metadata.copy()
        url_save.append('guardar')
        url_final.append('detail')
        if len(var) > 0:
            try:
                id = int(var[0])
                url_final.append(id)
                metadata['title'] = 'Editar ' + metadata['title']
            except:
                ret['error'] = 404
                return ret
        else:
            id = 0
            metadata['title'] = 'Nuevo ' + metadata['title']

        cls.breadcrumb.append({'url': functions.generar_url(
            url_final), 'title': metadata['title'], 'active': 'active'})
        if cls.contiene_tipos and 'tipo' not in get:
            url_final = ['home']

        if not administrador_model.verificar_sesion():
            url_final = ['login', 'index'] + url_final
        # verificar sesion o redireccionar a login
        url_return = functions.url_redirect(url_final)
        if url_return != '':
            ret['error'] = 301
            ret['redirect'] = url_return
            return ret

        # cabeceras y campos que se muestran en el detalle:
        # titulo,campo de la tabla a usar, tipo (ver archivo detalle.py funcion "field")

        # controlador de detalle
        detalle = detalle_class(metadata)
        configuracion = detalle.configuracion(metadata['modulo'])

        if 'error' in configuracion:
            ret['error'] = configuracion['error']
            ret['redirect'] = configuracion['redirect']
            return ret

        row = class_name.getById(id) if id != 0 else {}
        if cls.contiene_tipos:
            configuracion['campos']['tipo'] = {
                'title_field': 'tipo', 'field': 'tipo', 'type': 'hidden', 'required': True}
            row['tipo'] = get['tipo']

        if cls.contiene_hijos and 'idpadre' in configuracion['campos']:
            categorias = class_name.getAll()
            for c in categorias:
                if c[0] == id:
                    del c
                    break

            raiz = {0: 0, 'titulo': 'Raíz', 'idpadre': [-1]}
            categorias = raiz+categorias
            configuracion['campos']['idpadre']['parent'] = functions.crear_arbol(
                categorias, -1)
        elif cls.contiene_hijos or 'idpadre' in configuracion['campos']:
            configuracion['campos']['idpadre'] = {
                'title_field': 'idpadre', 'field': 'idpadre', 'type': 'hidden', 'required': True}
            if id == 0:
                if 'idpadre' in get:
                    row['idpadre'] = json.dumps([get['idpadre']])
                else:
                    row['idpadre'] = json.dumps([0])
        else:
            if 'idpadre' in configuracion['campos']:
                del configuracion['campos']['idpadre']

        if cls.class_parent != None:
            class_parent = cls.class_parent
            idparent = class_parent.idname

            is_array = True
            fields = table_model.getByname(class_name.table)
            if idparent in fields and fields[idparent]['tipo'] != 'longtext':
                is_array = False

            if idparent in configuracion['campos']:
                categorias = class_parent.getAll()
                if is_array:
                    configuracion['campos'][idparent]['parent'] = functions.crear_arbol(
                        categorias)
                else:
                    configuracion['campos'][idparent]['parent'] = categorias

            else:
                configuracion['campos'][idparent] = {
                    'title_field': idparent, 'field': idparent, 'type': 'hidden', 'required': True}
                if id == 0:
                    if idparent in get:
                        if is_array:
                            row[idparent] = json.dumps([get[idparent]])
                        else:
                            row[idparent] = int(get[idparent])
                    else:
                        if is_array:
                            row[idparent] = json.dumps([0])
                        else:
                            row[idparent] = 0
                else:
                    if is_array:
                        row[idparent] = json.dumps(row[idparent])
                    else:
                        row[idparent] = row[idparent]

        if 'idusuario' in configuracion['campos']:
            if id == 0 or row['idusuario'] == 0:
                usuarios = usuario_model.getAll({}, {'order': 'nombre ASC'})
                for u in usuarios:
                    u['titulo'] = u['nombre'] + \
                        ' (' + u['email'] + ')' + \
                        (': desactivado' if not u['estado'] else '')

                configuracion['campos']['idusuario']['parent'] = usuarios
            else:
                configuracion['campos']['idusuario']['type'] = 'hidden'

        if 'idpedidoestado' in configuracion['campos']:
            estados = pedidoestado_model.getAll({'tipo': get['tipo']})
            configuracion['campos']['idpedidoestado']['parent'] = estados
        if 'idmediopago' in configuracion['campos']:
            estados = mediopago_model.getAll()
            configuracion['campos']['idmediopago']['parent'] = estados

        if 'cookie_pedido' in configuracion['campos'] and id != 0:
            configuracion['campos']['cookie_pedido']['type'] = 'text'

        if 'direcciones' in configuracion['campos']:
            com = comuna_model.getAll()
            comunas = {}
            for c in com:
                if c['precio'] > 1:
                    r = region_model.getById(c['idregion'])
                    c['precio'] = r['precio']
                comunas[c[0]] = c

            configuracion['campos']['direcciones']['direccion_entrega'] = []
            lista_productos = producto_model.getAll( {'tipo': 1}, {'order': 'titulo ASC'})
            for key,lp in enumerate(lista_productos):
                portada = image.portada(lp['foto'])
                thumb_url = image.generar_url(portada, 'cart')
                lista_productos[key] = {'titulo': lp['titulo'], 'idproducto': lp['idproducto'], 'foto': thumb_url, 'precio': lp['precio_final'], 'stock': lp['stock']}
            configuracion['campos']['direcciones']['lista_productos'] = lista_productos

            lista_atributos = producto_model.getAll(
                {'tipo': 2}, {'order': 'titulo ASC'})

            for key,la in enumerate(lista_atributos):
                portada = image.portada(la['foto'])
                thumb_url = image.generar_url(portada, 'cart')
                lista_atributos[key] = {'titulo': la['titulo'], 'idproducto': la['idproducto'], 'foto': thumb_url}

            configuracion['campos']['direcciones']['lista_atributos'] = lista_atributos

            if id != 0:
                if 'idusuario' in row and row['idusuario'] != '':
                    direcciones_entrega = usuariodireccion_model.getAll(
                        {'idusuario': row['idusuario']})
                    for de in direcciones_entrega:
                        de['precio'] = comunas[de['idcomuna']]['precio']
                        de['titulo'] = de['titulo'] + \
                            ' (' + de['direccion'] + ')'

                    configuracion['campos']['direcciones']['direccion_entrega'] = direcciones_entrega

                pedidodirecciones = pedidodireccion_model.getAll(
                    {'idpedido': id})
                direcciones = []

                for d in pedidodirecciones:
                    new_d = {'idpedidodireccion': d['idpedidodireccion'], 'idusuariodireccion': d[
                        'idusuariodireccion'], 'precio': d['precio'], 'fecha_entrega': d['fecha_entrega']}
                    prod = pedidoproducto_model.getAll(
                        {'idpedido': id, 'idpedidodireccion': d[0]})
                    productos = []
                    for p in prod:
                        portada = image.portada(p['foto'])
                        thumb_url = image.generar_url(portada, '')
                        new_p = {'idpedidoproducto': p['idpedidoproducto'], 'idproductoatributo': p['idproductoatributo'], 'titulo': p['titulo'], 'mensaje': p['mensaje'],
                                 'idproducto': p['idproducto'], 'foto': thumb_url, 'precio': p['precio'], 'cantidad': p['cantidad'], 'total': p['total']}
                        productos.append(new_p)

                    new_d['productos'] = productos
                    new_d['cantidad'] = len(productos)
                    if new_d['cantidad'] == 0:
                        new_d['cantidad'] = ''

                    direcciones.append(new_d)

                row['direcciones'] = direcciones

        if 'fecha_pago' in row and row['fecha_pago'] == 0:
            row['fecha_pago'] = ''

        # informacion para generar la vista del detalle
        data = {
            'breadcrumb': cls.breadcrumb,
            'campos': configuracion['campos'],
            'row': row,
            'id': id if id != 0 else '',
            'current_url': functions.generar_url(url_final),
            'save_url': functions.generar_url(url_save),
            'list_url': functions.generar_url(url_list),
        }

        ret = detalle.normal(data)
        return ret

    def get_usuario(self):
        ret = {'headers': [
            ('Content-Type', 'application/json charset=utf-8')], 'body': ''}
        respuesta = {'exito': False, 'mensaje': ''}
        campos = app.post
        if 'idusuario' in campos:
            usuario = usuario_model.getById(campos['idusuario'])
            if len(usuario) > 0:
                com = comuna_model.getAll()
                comunas = {}
                for c in com:
                    if c['precio'] > 1:
                        r = region_model.getById(c['idregion'])
                        c['precio'] = r['precio']
                    comunas[c[0]] = c

                usuario = {0: usuario[0], 'nombre': usuario['nombre'],
                           'email': usuario['email'], 'telefono': usuario['telefono']}
                respuesta['usuario'] = usuario
                direcciones = usuariodireccion_model.getAll(
                    {'idusuario': usuario[0]})
                for d in direcciones:
                    d['precio'] = comunas[d['idcomuna']]['precio']

                respuesta['direcciones'] = direcciones
                respuesta['exito'] = True
            else:
                respuesta['mensaje'] = 'El usuario seleccionado no existe o esta desactivado'

        else:
            respuesta['mensaje'] = 'No se ha seleccionado un usuario'

        ret['body'] = json.dumps(respuesta, ensure_ascii=False)
        return ret

    def guardar(self):
        '''Guarda un pedido comprobando las direcciones y productos'''
        ret = {'headers': [
            ('Content-Type', 'application/json charset=utf-8')], 'body': ''}
        # Clase para enviar a controlador de detalle
        class_name = self.class_name
        campos = app.post['campos']
        respuesta = {'exito': False, 'mensaje': ''}
        if 'cookie_pedido_repetir' in campos:
            del campos['cookie_pedido_repetir']
        
        if 'datos_direcciones' in campos:
            direcciones = campos['datos_direcciones']
            del campos['datos_direcciones']
        else:
            direcciones=[]

        campos['total_original'] = campos['total']

        if campos['id'] == '':
            respuesta['id'] = class_name.insert(campos)
            respuesta['mensaje'] = "Creado correctamente"
        else:
            respuesta['id'] = int(class_name.update(campos))
            respuesta['mensaje'] = "Actualizado correctamente"

        if not isinstance(respuesta['id'], int):
            ret['body'] = json.dumps(respuesta['id'], ensure_ascii=False)
            return ret
        respuesta['exito'] = True
        pedido = pedido_model.getById(respuesta['id'])

        com = comuna_model.getAll()
        comunas = {}
        for c in com:
            if c['precio'] > 1:
                r = region_model.getById(c['idregion'])
                c['precio'] = r['precio']
            comunas[c[0]] = c

        dp = pedidodireccion_model.getAll({'idpedido': pedido[0]})
        direcciones_pedido = {}
        for d in dp:
            direcciones_pedido[d[0]] = d

        du = usuariodireccion_model.getAll({'idusuario': pedido['idusuario']})
        direcciones_usuario = {}
        for d in du:
            d['comuna'] = comunas[d['idcomuna']]
            direcciones_usuario[d[0]] = d

        pa = pedidoproducto_model.getAll({'idpedido': pedido[0]})
        productos_antiguos = {}
        for p in pa:
            productos_antiguos[p[0]] = p

        total_pedido = 0

        # procesar direcciones
        for d in direcciones.values():
            d['iddireccion']=int(d['iddireccion'])
            d['iddireccionpedido']=int(d['iddireccionpedido'])
            if not d['iddireccion'] in direcciones_usuario:
                respuesta['exito'] = False
                respuesta['mensaje'] = 'Una dirección no es valida, por favor recarga la pagina e intenta nuevamente'
                break
            else:
                du = direcciones_usuario[d['iddireccion']]

            productos = d['productos']
            if d['iddireccionpedido'] in direcciones_pedido:
                existe_direccion = True
                fields = table_model.getByname(pedidodireccion_model.table)
                new_d = database.create_data(
                    fields, direcciones_pedido[d['iddireccionpedido']])
                iddirecionpeddido = direcciones_pedido[d['iddireccionpedido']][0]
                del direcciones_pedido[d['iddireccionpedido']]
                new_d['fecha_entrega'] = d['fecha_entrega']
            else:
                existe_direccion = False
                new_d = d
                new_d['cookie_direccion'] = pedido['cookie_pedido'] + \
                    '-' + functions.generar_pass(2)
                new_d['idpedido'] = pedido[0]
                new_d['idusuariodireccion'] = du[0]

            # 4= pedido pagado
            if pedido['idpedidoestado'] != 4:
                # 9=envio no pagado aun
                new_d['idpedidoestado'] = 9
            else:
                # 5=preparango producto
                new_d['idpedidoestado'] = 5

            # NEW_D= Direccion de envio actualizada en el pedido
            new_d['precio'] = du['comuna']['precio']

            new_d['nombre'] = du['nombre']
            new_d['telefono'] = du['telefono']
            new_d['referencias'] = du['referencias']
            new_d['direccion_completa'] = du['direccion'] + \
                ', ' + du['comuna']['titulo'] + ''
            new_d['direccion_completa'] += ', villa ' + \
                du['villa'] if du['villa'] != '' else ''
            new_d['direccion_completa'] += ', edificio ' + \
                du['edificio'] if du['edificio'] != '' else ''
            new_d['direccion_completa'] += ', departamento ' + \
                du['departamento'] if du['departamento'] != '' else ''
            new_d['direccion_completa'] += ', condominio ' + \
                du['condominio'] if du['condominio'] != '' else ''
            new_d['direccion_completa'] += ', casa ' + \
                du['casa'] if du['casa'] != '' else ''
            new_d['direccion_completa'] += ', empresa ' + \
                du['empresa'] if du['empresa'] != '' else ''

            if existe_direccion:
                new_d['id'] = iddirecionpeddido
                idpedidodireccion = pedidodireccion_model.update(new_d)
            else:
                idpedidodireccion = pedidodireccion_model.insert(new_d)

            total_pedido += new_d['precio']

            for p in productos.values():
                p['idproductopedido']=int(p['idproductopedido'])
                p['cantidad']=int(p['cantidad'])
                cantidad_antigua = 0
                if p['idproductopedido'] in productos_antiguos:
                    existe = True
                    fields = table_model.getByname(pedidoproducto_model.table)
                    new_p = database.create_data( fields, productos_antiguos[p['idproductopedido']])

                    del productos_antiguos[p['idproductopedido']]
                    if new_p['idproducto'] != p['idproducto']:
                        change = True
                    else:
                        change = False

                    cantidad_antigua = new_p['cantidad']
                    new_p['idproducto'] = p['idproducto']
                    new_p['cantidad'] = p['cantidad']
                    new_p['idproductoatributo'] = p['idproductoatributo']
                    new_p['mensaje'] = p['mensaje']
                else:
                    existe = False
                    change = True
                    new_p = p
                    new_p['idpedido'] = pedido[0]
                    del new_p['idproductopedido']

                producto_detalle = producto_model.getById(new_p['idproducto'])
                if len(producto_detalle) == 0:
                    respuesta['exito'] = False
                    respuesta['mensaje'] = 'Un producto no es valido, por favor recarga la pagina e intenta nuevamente'
                    ret['body'] = json.dumps(respuesta, ensure_ascii=False)
                    return ret
                

                producto_detalle['stock'] -= (new_p['cantidad'] - cantidad_antigua)

                if change:
                    new_p['titulo'] = producto_detalle['titulo']
                    new_p['precio'] = producto_detalle['precio_final']

                new_p['idpedidodireccion'] = idpedidodireccion
                atributo = producto_model.getById(new_p['idproductoatributo'])
                new_p['titulo_atributo'] = atributo['titulo']
                new_p['total'] = new_p['precio'] * new_p['cantidad']

                if existe:
                    new_p['id'] = p['idproductopedido']
                    new_p['foto'] = json.dumps(new_p['foto'])
                    idpedidoproducto = pedidoproducto_model.update(new_p)
                else:
                    idpedidoproducto = pedidoproducto_model.insert(new_p)

                if change:
                    new_p['id'] = idpedidoproducto
                    portada = image.portada(producto_detalle['foto'])
                    copiar = image.copy( portada, new_p['id'], pedidoproducto_model.table, '', '', 'cart')
                    if copiar['exito']:
                        new_p['foto'] = json.dumps(copiar['file'])
                        idpedidoproducto = pedidoproducto_model.update(new_p)
                    else:
                        respuesta = copiar
                        ret['body'] = json.dumps(respuesta, ensure_ascii=False)
                        return ret

                producto_model.update(
                    {'id': new_p['idproducto'], 'stock': producto_detalle['stock']})
                total_pedido += new_p['total']

        # borrar productos y direcciones si fueron eliminados en la vista
        for pa in productos_antiguos:
            producto_detalle = producto_model.getById(pa['idproducto'])
            producto_detalle['stock'] += (pa['cantidad'])
            producto_detalle['id'] = pa['idproducto']
            producto_model.update(
                {'id': pa['idproducto'], 'stock': producto_detalle['stock']})
            pedidoproducto_model.delete(pa[0])

        for dp in direcciones_pedido:
            pedidodireccion_model.delete(dp[0])

        if pedido['total'] != total_pedido:
            campos['total_original'] = total_pedido
            campos['id'] = pedido[0]
            respuesta['id'] = class_name.update(campos)

        ret['body'] = json.dumps(respuesta, ensure_ascii=False)
        return ret
