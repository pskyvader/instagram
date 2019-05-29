from core.functions import functions
#from core.view import view
from core.app import app
from core.image import image
from app.models.administrador import administrador as administrador_model
from app.models.moduloconfiguracion import moduloconfiguracion as moduloconfiguracion_model
from app.models.modulo import modulo as modulo_model
from app.models.pedidoestado import pedidoestado as pedidoestado_model


class aside:

    def normal(self):
        ret = {'body': []}
        if 'ajax' not in app.post:
            administrador = administrador_model.getById(
                app.session[administrador_model.idname + app.prefix_site])
            tipo_admin = administrador["tipo"]
            moduloconfiguracion = moduloconfiguracion_model.getAll(
                {'estado': True, 'aside': True})
            modulo = modulo_model.getAll({'aside': True})

            mod = {}
            for m in modulo:
                if not m['idmoduloconfiguracion'] in mod:
                    mod[m['idmoduloconfiguracion']] = []
                mod[m['idmoduloconfiguracion']].append(m)

            current_url = functions.current_url()

            menu = []
            url = functions.generar_url(["home"], False)
            active = (url == current_url)
            menu.append({'url': url, 'icon': 'home', 'title': 'Home',
                         'has_submenu': False, 'active': active, 'separador': False})

            for cm in moduloconfiguracion:
                if cm['module'] == "pedido":
                    pedidoestado = pedidoestado_model.getAll(
                        {'tipo': 1}, {'order': 'orden ASC'})
                    tmp = mod[cm[0]]
                    mod[cm[0]] = []
                    for t in tmp:
                        t['idpedidoestado'] = 0
                        t['titulo'] = 'Todos'
                        mod[cm[0]].append(t.copy())
                        for pe in pedidoestado:
                            t['idpedidoestado'] = pe[0]
                            t['titulo'] = pe['titulo']
                            mod[cm[0]].append(t.copy())

                if cm[0] not in mod:
                    if cm['module'] == 'separador':
                        menu.append({'title': cm['titulo'], 'separador': True})
                elif len(mod[cm[0]]) == 1:
                    modulo = mod[cm[0]][0]
                    estados = modulo['estado'][0]['estado']
                    if estados[str(tipo_admin)] == 'true':
                        extra = {}
                        if cm['tipos']:
                            extra['tipo'] = modulo['tipo']

                        if modulo['hijos']:
                            extra['idpadre'] = 0

                        if cm['module'] == "pedido":
                            extra['idpedidoestado'] = modulo['idpedidoestado']

                        if len(extra) == 0:
                            extra = False

                        url = functions.generar_url([cm['module']], extra)
                        active = (url == current_url)
                        menu.append({'url': url, 'icon': cm['icono'], 'title': modulo['titulo'],
                                     'has_submenu': False, 'active': active, 'separador': False})
                else:
                    active = False
                    me = {'icon': cm['icono'], 'title': cm['titulo'], 'has_submenu': True, 'submenu': [
                    ], 'active': active, 'separador': False}
                    for m in mod[cm[0]]:
                        modulo = m
                        estados = modulo['estado'][0]['estado']
                        if estados[str(tipo_admin)] == 'true':
                            extra = {}
                            if cm['tipos']:
                                extra['tipo'] = modulo['tipo']

                            if modulo['hijos']:
                                extra['idpadre'] = 0

                            if cm['module'] == "pedido":
                                extra['idpedidoestado'] = modulo['idpedidoestado']

                            if len(extra) == 0:
                                extra = False

                            url = functions.generar_url([cm['module']], extra)
                            active = (url == current_url)
                            me['submenu'].append(
                                {'url': url, 'sub_title': modulo['titulo'], 'active': active})
                            if active:
                                me['active'] = True

                    if len(me['submenu']) > 0:
                        menu.append(me)

            if tipo_admin == 1:
                menu.append(
                    {'title': 'Solo para desarrollo', 'separador': True})
                url = functions.generar_url(["moduloconfiguracion"], False)
                active = (url == current_url)
                me = {'url': url, 'icon': 'mode_edit', 'title': 'Modulos',
                      'has_submenu': True, 'submenu': [], 'active': active, 'separador': False}
                me['submenu'].append(
                    {'url': url, 'sub_title': 'TODOS', 'active': active})

                mc = moduloconfiguracion_model.getAll()
                for m in mc:
                    url = functions.generar_url(
                        ['modulo'], {'idmoduloconfiguracion': m[0]})
                    active = (url == current_url)
                    me['submenu'].append(
                        {'url': url, 'sub_title': m['titulo'], 'active': active})

                menu.append(me)

                url = functions.generar_url(["table"], False)
                active = (url == current_url)
                menu.append({'url': url, 'icon': 'table', 'title': 'Tablas',
                             'has_submenu': False, 'active': active, 'separador': False})

                url = functions.generar_url(
                    ["configuracion_administrador"], False)
                active = (url == current_url)
                menu.append({'url': url, 'icon': 'settings_applications', 'title': 'Configuracion Administrador',
                             'has_submenu': False, 'active': active, 'separador': False})

            data = {}
            data['menu'] = menu
            data['name'] = administrador["nombre"]
            data['email'] = administrador["email"]
            data['url_admin'] = functions.generar_url(
                ["administrador", "detail", administrador[0]], {'tipo': tipo_admin})
            data['img_admin'] = image.generar_url(
                administrador["foto"][0], 'profile')

            ret['body'].append(('aside', data))
        return ret
