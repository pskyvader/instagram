class cache:
    data = []
    cacheable = None
    cacheable_config = None
    url_cache=[]

    @staticmethod
    def set_cache(cacheable: bool):
        if cache.cacheable!=False:
            cache.cacheable = cacheable

    @staticmethod
    def add_cache(content):
        from .app import app
        if cache.cacheable:
            cache.data.append(content)

    @staticmethod
    def delete_cache():
        import shutil
        import os
        from .app import app
        from .view import view

        directory = app.get_dir(True) + "cache/"
        if os.path.exists(directory):
            shutil.rmtree(directory)

        directory = app.get_dir(True) + "uploads/cache/"
        if os.path.exists(directory):
            shutil.rmtree(directory)

        directory = view.get_theme() + "cache/"
        if os.path.exists(directory):
            shutil.rmtree(directory)

        config = app.get_config()
        directory = app.app_dir + "views/front/themes/" + config["theme"] + "/cache/"
        if os.path.exists(directory):
            shutil.rmtree(directory)

        directory = (
            app.app_dir + "views/back/themes/" + config["theme_back"] + "/cache/"
        )
        if os.path.exists(directory):
            shutil.rmtree(directory)

    @staticmethod
    def get_cache():
        from .app import app
        from .functions import functions
        from pathlib import Path

        if not app.front:
            cache.cacheable = False
        else:
            cache.cacheable = True

        ruta = functions.generar_url(cache.url_cache)
        current = functions.current_url()

        if cache.url_cache=='' or ruta != current:
            return ""
        if cache.cacheable_config == None:
            config = app.get_config()
            cache.cacheable_config = config["cache"] if "cache" in config else True
            if not cache.cacheable_config:
                cache.cacheable = False

        if cache.cacheable:
            folder = app.get_dir(True) + "cache/"
            name = cache.file_name()
            my_file = Path(folder + name)
            if my_file.is_file():
                return my_file

        return ""

    @staticmethod
    def save_cache():
        from .app import app
        from .functions import functions
        import os
        from gzip import compress

        ruta = functions.generar_url(cache.url_cache)
        current = functions.current_url()
        
        if cache.url_cache!='' and ruta == current and cache.cacheable:
            folder = app.get_dir(True) + "cache/"
            if not os.path.exists(folder):
                os.makedirs(folder)

            if os.access(folder, os.W_OK):
                name = cache.file_name()
                if name != "":
                    f = "".join(cache.data)
                    cache.data=[]
                    f = bytes(f, "utf-8")
                    f = compress(f)

                    file_write = open(folder + name, "wb")
                    file_write.write(f)
                    file_write.close()

    @staticmethod
    def file_name():
        from .app import app
        from .functions import functions

        name = "-".join(cache.url_cache)
        n = name.split(".", 1)
        if len(n) > 1:
            return ""

        for key, u in app.get.items():
            ext = "__" + key + "-" + u
            ext = functions.url_amigable(ext)
            name += ext

        post = app.post.copy()
        if "ajax" in post:
            name += "__ajax"
            del post['ajax']

        if len(post) > 0:
            return ""

        return name

    @staticmethod
    def serve_cache(resource_url, theme, resource):
        from core.functions import functions
        from pathlib import Path
        import os
        import mimetypes
        import datetime

        ret = {"body": ""}
        my_file = Path(resource_url)
        if not my_file.is_file():
            ret = {"error": 404}
        else:
            ret["is_file"] = True
            mime = mimetypes.guess_type(resource_url, False)[0]
            if mime == None:
                mime = "text/plain"
            extension = mimetypes.guess_extension(mime)
            expiry_time = datetime.datetime.utcnow() + datetime.timedelta(100)
            ret["headers"] = [
                ("Content-Type", mime + "; charset=utf-8"),
                ("Expires", expiry_time.strftime("%a, %d %b %Y %H:%M:%S GMT")),
                ("Accept-encoding", "gzip,deflate"),
                ("Content-Encoding", "gzip"),
            ]
            cache_file = (
                theme
                + "cache/"
                + str(functions.fecha_archivo(resource_url, True))
                + "-"
                + resource.replace("/", "-")
            )

            if not os.path.exists(theme + "cache/"):
                os.makedirs(theme + "cache/")

            my_file = Path(cache_file)
            if my_file.is_file():
                ret["file"] = cache_file
            else:
                from gzip import compress

                test = os.listdir(theme + "cache/")
                for item in test:
                    if "resources" in resource and item.endswith(extension):
                        os.remove(os.path.join(theme + "cache/", item))
                    elif item.endswith(resource):
                        os.remove(os.path.join(theme + "cache/", item))
                f = open(resource_url, "rb").read()
                f = compress(f)

                file_write = open(cache_file, "wb")
                file_write.write(f)
                file_write.close()
                ret["file"] = cache_file

        return ret
