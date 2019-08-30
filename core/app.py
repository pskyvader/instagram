import sys
import os
from .view import view
import json
from pathlib import Path
import importlib


class app:
    config = {}
    app_dir = "app/"
    controller_dir = app_dir + "controllers/"
    view_dir = app_dir + "views/"
    title = ""
    prefix_site = ""
    url = {}
    front = True
    path = ""
    root = ""
    environ = {}
    get = {}
    root_url = ""
    client_ip = ""
    idseo = 0

    def __init__(self, root):
        import locale

        locale.setlocale(locale.LC_ALL, "es_CL.UTF-8")
        app.root = root + "/"

    def init(self, environ):
        from .cache import cache
        from .functions import functions

        # from datetime import datetime
        # init_time = datetime.now()

        app.environ = environ
        data_return = {}
        app.get = self.parse_get(app.environ["QUERY_STRING"])
        app.post = self.parse_post()
        app.session = app.environ["beaker.session"]
        app.client_ip = self.parse_ip(app.environ)
        url = self.parse_url(environ["PATH_INFO"])

        config = self.get_config()
        app.title = config["title"]
        app.prefix_site = functions.url_amigable(app.title)

        app.root_url = environ["SERVER_NAME"].replace("www.", "")
        # app.root_url = environ["HTTP_HOST"].replace("www.", "")
        subdirectorio = config["dir"]
        https = "https://" if config["https"] else "http://"
        www = "www." if config["www"] else ""
        port = environ["SERVER_PORT"]
        if port != 80:
            app.root_url += ":" + str(port)

        app.path = https + www + app.root_url + "/"
        if subdirectorio != "":
            app.path += subdirectorio + "/"
            subdirectorio = "/" + subdirectorio + "/"
        else:
            subdirectorio = "/"

        if url[0] == config["admin"]:
            app.front = False
            del url[0]
            if len(url) == 0:
                url = ["home"]
        else:
            app.front = True

        app.url["base"] = app.path
        app.url["admin"] = app.path + config["admin"] + "/"

        app.url["base_dir"] = app.root
        app.url["admin_dir"] = app.root + config["admin"] + "/"

        app.url["base_sub"] = subdirectorio
        app.url["admin_sub"] = subdirectorio + config["admin"] + "/"

        if app.front:
            app.controller_dir = (
                app.app_dir + "controllers/front/themes/" + config["theme"] + "/"
            )
            app.view_dir = app.app_dir + "views/front/themes/" + config["theme"] + "/"
        else:
            app.path = app.url["admin"]
            app.controller_dir = (
                app.app_dir
                + "controllers/"
                + "back/themes/"
                + config["theme_back"]
                + "/"
            )
            app.view_dir = (
                app.app_dir + "views/" + "back/themes/" + config["theme_back"] + "/"
            )

        view.set_theme(app.root + app.view_dir)

        file_cache = cache.get_cache()
        if file_cache != "":
            response = {
                "file": file_cache,
                "is_file": True,
                "body": "",
                "headers": [
                    ("Content-Type", "text/html charset=utf-8"),
                    ("Accept-encoding", "gzip,deflate"),
                    ("Content-Encoding", "gzip"),
                ],
            }
        else:
            controller = app.controller_dir + url[0]
            my_file = Path(app.root + controller + ".py")
            if my_file.is_file():
                current_module = importlib.import_module(controller.replace("/", "."))
                current_module = getattr(current_module, url[0])
                current_module = current_module()
                del url[0]
                # returns {'body':[],'headers':str} or {'error':int,...'redirect':str}
                response = current_module.init(url.copy())
            else:
                response = {"error": 404}

        if "headers" not in response:
            response["headers"] = [("Content-Type", "text/html charset=utf-8")]

        if "error" in response:
            if response["error"] == 301:
                if config["debug"]:
                    data_return["status"] = "200 OK"
                    response["body"] = (
                        '<html><body>redirige <a href="'
                        + response["redirect"]
                        + '">'
                        + response["redirect"]
                        + "</a></body></html>"
                    )
                else:
                    data_return["status"] = "301 Moved Permanently"
                    response["headers"] = [("Location", response["redirect"])]
                    response["body"] = ""
            else:
                data_return["status"] = "404 Not Found"
                if config["debug"]:
                    error_file = str(my_file)
                else:
                    error_file = ""

                controller = app.controller_dir + "error"
                my_file = Path(app.root + controller + ".py")
                if my_file.is_file():
                    current_module = importlib.import_module(
                        controller.replace("/", ".")
                    )
                    current_module = getattr(current_module, "error")
                    current_module = current_module()
                    response_error = current_module.init(["index", error_file])
                    # response_error = current_module.index(str(error_file))
                    response["body"] = response_error["body"]
                else:
                    response["body"] = (
                        "<html><body>No encontrado " + error_file + "</body></html>"
                    )
        else:
            data_return["status"] = "200 OK"

        if "is_file" in response:
            data_return["is_file"] = response["is_file"]
        if "file" in response:
            data_return["file"] = response["file"]

        # if data_return['status']=='200 OK':
        # print('antes de render', (datetime.now()-init_time).total_seconds()*1000)
        # init_time=datetime.now()

        if isinstance(response["body"], list):
            data_return["response_body"] = view.render(response["body"])
            cache.save_cache()
        else:
            data_return["response_body"] = response["body"]

        data_return["headers"] = response["headers"]
        for cookie in functions.cookies:
            data_return["headers"].append(("Set-Cookie", cookie))
        # if data_return['status']=='200 OK':
        # print('despues de render', (datetime.now()-init_time).total_seconds()*1000)
        return data_return

    @staticmethod
    def parse_url(url):
        from app.models.seo import seo as seo_model
        from .cache import cache

        config = app.get_config()
        url = url.lstrip("/")

        if url != "":
            url = " ".join(url.split("/")).split()
        else:
            url = []

        cache.url_cache = url.copy()

        if len(url) > 0:
            if url[0] == "manifest.js":
                url[0] = "manifest"
            elif url[0] == "sw.js":
                url[0] = "sw"
            elif (
                url[0] == "log.json" or url[0] == "icon.txt" or url[0] == "sitemap.xml"
            ):
                url = ["static_file"] + url
            elif url[0] == "favicon.ico":
                url[0] = "favicon"
            elif url[0] == config["admin"]:
                if len(url) > 1:
                    if url[1] == "manifest.js":
                        url[1] = "manifest"
                    elif url[1] == "sw.js":
                        url[1] = "sw"
                    elif (
                        url[1] == "log.json"
                        or url[1] == "icon.txt"
                        or url[1] == "sitemap.xml"
                    ):
                        url_tmp = [url[0]]
                        del url[0]
                        url = url_tmp + ["static_file"] + url
                    elif url[1] == "favicon.ico":
                        url[1] = "favicon"
            else:
                seo = seo_model.getAll({"url": url[0]}, {"limit": 1})
                if len(seo) == 1:
                    url[0] = seo[0]["modulo_front"]
                    app.idseo = seo[0][0]
        else:
            url = [""]
            seo = seo_model.getById(1)
            if len(seo) > 0:
                url[0] = seo["modulo_front"]
                app.idseo = seo[0]

        return url

    @staticmethod
    def parse_get(query_string):
        from cgi import parse_qs

        get = dict(parse_qs(query_string))
        if "url" in get:
            del get["url"]
        for k, u in get.items():
            if len(u) == 1:
                get[k] = u[0]
        get = app.format_array(get)
        get = app.parse_values(get)
        return get

    @staticmethod
    def parse_post():
        from cgi import FieldStorage
        from io import BytesIO

        post = {}
        if app.environ["REQUEST_METHOD"] == "POST":
            post_env = app.environ.copy()
            post_env["QUERY_STRING"] = ""
            post_env["CONTENT_LENGTH"] = int(app.environ.get("CONTENT_LENGTH", 0))
            buffer = post_env["wsgi.input"].read(post_env["CONTENT_LENGTH"])
            p = FieldStorage(
                fp=BytesIO(buffer), environ=post_env, keep_blank_values=True
            )
            if p.list != None:
                post = app.post_field(p)

        post = app.format_array(post)
        post = app.parse_values(post)
        return post

    @staticmethod
    def post_field(p):
        from cgi import MiniFieldStorage, FieldStorage, escape
        from .functions import functions

        post = {}
        try:
            for key in p.keys():
                if (
                    isinstance(p[key], FieldStorage)
                    and p[key].file
                    and p[key].filename != None
                ):
                    if not "file" in post:
                        post["file"] = []
                    tmpfile = p[key].file.read()
                    name = escape(p[key].filename)
                    mime = functions.get_content_type_by_filename(name)
                    if mime == None:
                        mime = "text/plain"
                    post["file"].append(
                        {"name": name, "type": mime, "tmp_name": tmpfile}
                    )
                elif isinstance(p[key], MiniFieldStorage) or isinstance(
                    p[key], FieldStorage
                ):
                    post[key] = p[key].value
                elif isinstance(p[key], list):
                    tmp_list = []
                    for a in p[key]:
                        if isinstance(a, MiniFieldStorage):
                            tmp_list.append(a.value)
                        else:
                            tmp_list.append(a)
                    post[key] = tmp_list
                else:
                    post[key] = p[key]
        except Exception as error:
            # print('Error al obtener post: ' + repr(error) + repr(p)
            raise RuntimeError("Error al obtener post: " + repr(error) + repr(p))
        return post

    @staticmethod
    def format_array(var_original: dict):
        var = var_original.copy()
        var_copy = var.copy()
        aux = {}
        for k, i in var_copy.items():
            # si existe simbolo de array
            if "[" in k:
                # separar key principal de key dentro de array
                final_key, rest = str(k).split("[", 1)
                if rest != "":
                    if final_key not in aux:
                        aux[final_key] = {}

                    # comprobar si existe simbolo de cerrado, sino se guarda directamente
                    if rest.find("]") == -1:
                        aux[final_key][rest] = i
                    # comprobar si existe mas de un valor en sub key, sino se recupera el primer y unico valor
                    elif rest.find("[") == -1:
                        rest = str(rest).split("]", 1)[0]
                        aux[final_key][rest] = i
                    else:
                        if rest.find("]") < rest.find("["):
                            rest1, rest2 = str(rest).split("]", 1)
                            aux[final_key][rest1 + rest2] = i
                        else:
                            print(
                                "error de formato, formato aceptado: a[b][c][d]=valor"
                            )
                            break
                    aux[final_key] = app.format_array(aux[final_key])
                else:
                    aux[final_key] = i
                del var[k]
            elif k == "":
                final_key = len(var_copy) - 1
                aux[final_key] = i
                del var[k]

        var = app.merge(var, aux)
        if len(var) == 1:
            key, value = next(iter(var.items()))
            if isinstance(key, int) and key == 0:
                var = value
        return var

    @staticmethod
    def parse_values(var: dict):
        var_copy = var.copy()
        if isinstance(var_copy, list):
            for i in var_copy:
                if isinstance(i, str):
                    try:
                        aux_var = json.loads(i)
                        if isinstance(aux_var, dict) or isinstance(aux_var, list):
                            i = aux_var
                    except:
                        pass
                elif isinstance(i, dict) or isinstance(i, list):
                    i = app.parse_values(i)
        elif isinstance(var_copy, dict):
            for k, i in var_copy.items():
                if isinstance(i, str):
                    try:
                        aux_var = json.loads(i)
                        if isinstance(aux_var, dict) or isinstance(aux_var, list):
                            var_copy[k] = app.parse_values(aux_var)
                    except:
                        pass
                elif isinstance(i, dict) or isinstance(i, list):
                    var_copy[k] = app.parse_values(i)
        elif isinstance(var_copy, str):
            try:
                aux_var = json.loads(var_copy)
                if isinstance(aux_var, dict) or isinstance(aux_var, list):
                    var_copy = app.parse_values(aux_var)
            except:
                pass

        return var_copy

    @staticmethod
    def parse_ip(environ):
        try:
            return str(environ["HTTP_X_FORWARDED_FOR"].split(",")[-1]).strip()
        except KeyError:
            return environ["REMOTE_ADDR"]

    @staticmethod
    def merge(a, b, path=None):
        "merges b into a"
        if path is None:
            path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    app.merge(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass  # same leaf value
                else:
                    raise Exception("Conflict at %s" % ".".join(path + [str(key)]))
            else:
                a[key] = b[key]
        return a

    @staticmethod
    def get_config():
        if len(app.config) == 0:
            with open(app.app_dir + "config/config.json") as f:
                app.config = json.load(f)
        return app.config

    @staticmethod
    def get_dir(front=False):
        if app.front or front:
            return app.url["base_dir"]
        else:
            return app.url["admin_dir"]

    @staticmethod
    def get_url(front=False):
        if app.front or front:
            return app.url["base"]
        else:
            return app.url["admin"]

