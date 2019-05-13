from pathlib import Path
import os
import json


class view:
    extension = "html"
    theme_front = ""
    theme_back = ""
    resources_front = {}
    resources_back = {}
    html = """
        <html>
            %(content)s
        </html>
    """

    @staticmethod
    def render(template_list, minify=True, theme=""):
        """Renderiza las vistas de la lista enviadas, las comprime y la retorna en un string"""
        from .app import app
        from .cache import cache
        from jinja2 import (
            Environment,
            FileSystemLoader,
            FileSystemBytecodeCache,
            DebugUndefined,
        )

        if theme == "":
            theme = view.get_theme()

        env = Environment(
            loader=FileSystemLoader(theme),
            bytecode_cache=FileSystemBytecodeCache(
                directory=app.get_dir(True) + "tmp/"
            ),
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=DebugUndefined,
        )

        # custom filter
        def phone_number(number):
            """Convert a 10 character string into (xxx) xxx-xxxx."""
            base1 = -7 if len(number) == 10 else -8
            base2 = -4
            first = number[:base1]
            second = number[base1:base2]
            third = number[base2:]
            return first + " " + second + " " + third

        env.filters["phone_number"] = phone_number
        # custom filter

        for template, data in template_list:
            template_url = theme + template + "." + view.extension
            my_file = Path(template_url)
            if not my_file.is_file():
                body = view.html % {  # Fill the above html template in
                    "content": " <body>Error: El archivo "
                    + template_url
                    + " no existe </body>"
                }
                return body

        body = ""
        for template, data in template_list:
            body += view.render_unit(env, template, data)

        if minify and cache.cacheable:
            body = view.compress(body, "html")

        cache.add_cache(body)

        return body

    @staticmethod
    def render_unit(env, template, data):
        if isinstance(data, dict):
            data2 = {}
            for k, d in data.items():
                if isinstance(d, dict) or isinstance(d, list) or isinstance(d, tuple):
                    d = view.render_unit(env, "", d)
                data2[k] = d
            data = data2
        elif isinstance(data, list):
            data2 = []
            for d in data:
                if isinstance(d, dict) or isinstance(d, list) or isinstance(d, tuple):
                    d = view.render_unit(env, "", d)
                data2.append(d)
            data = data2
            if all(isinstance(x, str) for x in data):
                data = "".join(data)
        elif isinstance(data, tuple):
            data = view.render_unit(env, data[0], data[1])

        if template != "" and isinstance(data, dict):
            templ = env.get_template(template + "." + view.extension)
            content = templ.render(data)
            return content
        else:
            return data

    @staticmethod
    def render_template(template_bytes, data):
        from jinja2 import Template

        template = Template(template_bytes)
        content = template.render(data)
        return content

    @staticmethod
    def css(combine=True, array_only=False):
        from core.functions import functions
        from core.app import app

        if "ajax" in app.post:
            return ""

        theme = view.get_theme()
        base_url = (
            app.url["base"] + "static/" if app.front else app.url["admin"] + "static/"
        )
        css, locales, no_combinados, nuevo, error = view.recorrer(
            "css", combine, theme, base_url
        )

        if error != "":
            return error

        if combine and len(locales) > 0:
            locales = view.combine_resources("css", locales, theme, base_url, nuevo)

        css = no_combinados + locales + css

        if array_only:
            return [css, nuevo]
        else:
            data = {}
            data["js"] = []
            data["is_css"] = True
            data["css"] = css
            return ("resources", data)

    @staticmethod
    def js(combine=True, array_only=False):
        from core.functions import functions
        from core.app import app

        if "ajax" in app.post:
            return ""

        theme = view.get_theme()
        base_url = (
            app.url["base"] + "static/" if app.front else app.url["admin"] + "static/"
        )
        js, locales, no_combinados, nuevo, error = view.recorrer(
            "js", combine, theme, base_url
        )

        if error != "":
            return error

        if combine and len(locales) > 0:
            locales = view.combine_resources("js", locales, theme, base_url, nuevo)

        js = no_combinados + locales + js

        if array_only:
            return [js, nuevo]
        else:
            data = {}
            data["css"] = []
            data["is_css"] = False
            data["js"] = js
            return ("resources", data)

    @staticmethod
    def set_theme(theme):
        from core.app import app

        if app.front:
            view.theme_front = theme
        else:
            view.theme_back = theme

    @staticmethod
    def get_theme():
        from core.app import app

        if app.front:
            return view.theme_front
        else:
            return view.theme_back

    @staticmethod
    def recorrer(type_resource="css", combine=True, theme="", base_url=""):
        from core.functions import functions
        from core.app import app

        if app.front:
            if len(view.resources_front) == 0:
                with open(theme + "resources.json") as f:
                    view.resources_front = json.load(f)
            resources = view.resources_front
        else:
            if len(view.resources_back) == 0:
                with open(theme + "resources.json") as f:
                    view.resources_back = json.load(f)
            resources = view.resources_back

        resource = []
        locales = []
        no_combinados = []
        nuevo = 0
        error = ""
        for res in resources[type_resource]:
            c = res.copy()
            c["is_content"] = False
            if c["local"]:
                c["url_tmp"] = c["url"]
                c["url"] = theme + c["url"]
                my_file = Path(c["url"])
                if my_file.is_file():
                    if (
                        combine
                        and c["combine"]
                        and (
                            (type_resource == "js" and not c["defer"])
                            or type_resource == "css"
                        )
                    ):
                        fecha = functions.fecha_archivo(c["url"], True)
                        if fecha > nuevo:
                            nuevo = fecha
                        locales.append(c)
                    else:
                        if type_resource == "css" and os.path.getsize(c["url"]) < 8000:
                            c["content_css"] = open(c["url"], "r").read()
                            c["is_content"] = True
                        else:
                            c["url"] = base_url + functions.fecha_archivo(
                                c["url"], False, c["url_tmp"]
                            )
                        no_combinados.append(c)
                else:
                    if app.config["debug"]:
                        error = "Recurso no existe:" + c["url"]
            else:
                c["url"] = functions.ruta(c["url"])
                resource.append(c)
        return resource, locales, no_combinados, nuevo, error

    @staticmethod
    def combine_resources(
        type_resource="css", locales={}, theme="", base_url="", nuevo=0
    ):
        from .functions import functions
        from .cache import cache
        from os import path, makedirs

        dir_resources = theme + "custom_resources/"
        if not path.exists(dir_resources):
            makedirs(dir_resources)
        file = "resources-" + str(nuevo) + "-" + str(len(locales)) + "." + type_resource
        my_file = Path(dir_resources + file)
        if my_file.is_file():
            if functions.get_cookie("loaded_" + type_resource) != False:
                defer = False
            else:
                functions.set_cookie("loaded_" + type_resource, True, (31536000))
                defer = True

            locales = [
                {
                    "url": base_url + "custom_resources/" + file,
                    "media": "all",
                    "defer": defer,
                    "is_content": False,
                }
            ]
        else:
            cache.delete_cache()
            if functions.get_cookie("loaded_" + type_resource) != False:
                functions.set_cookie("loaded_" + type_resource, True, (31536000))

            if os.access(dir_resources, os.R_OK):
                combine_files = ""
                for l in locales:
                    tmp = open(l["url"], "r", encoding="utf-8").read()
                    combine_files += "\n" + tmp

                test = os.listdir(dir_resources)
                for item in test:
                    if item.endswith("." + type_resource):
                        os.remove(os.path.join(dir_resources, item))
                file_write = open(dir_resources + file, "w", encoding="utf-8")
                combine_files = view.compress(combine_files, type_resource)
                file_write.write(combine_files)
                file_write.close()
                locales = [
                    {
                        "url": base_url + "custom_resources/" + file,
                        "media": "all",
                        "defer": True,
                        "is_content": False,
                    }
                ]
            else:
                for l in locales:
                    l["url"] = base_url + functions.fecha_archivo(
                        l["url"], False, l["url_tmp"]
                    )
        return locales

    @staticmethod
    def compress(combine_files, type_resource):
        if type_resource == "css":
            from csscompressor import compress

            combine_files = compress(combine_files)
        elif type_resource == "js":
            from jsmin import jsmin

            combine_files = jsmin(combine_files)
        elif type_resource == "html":
            from htmlmin import minify

            combine_files = minify(combine_files, True, True, True)
        return combine_files
