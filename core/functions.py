from .app import app
from pathlib import Path
from urllib.parse import urlencode
from os.path import getmtime


class functions():
    cookies = []
    timezone = 'America/Santiago'
    @staticmethod
    def get_cookie(find_cookie=''):
        from http import cookies
        c = cookies.SimpleCookie()
        if 'HTTP_COOKIE' in app.environ:
            c.load(app.environ['HTTP_COOKIE'])
            if find_cookie != '':
                if find_cookie in c:
                    return c[find_cookie].value
                else:
                    return False
            else:
                coo = {}
                for key, cookie in c.items():
                    coo[key] = cookie.value
                return coo
        else:
            if find_cookie != '':
                return False
            else:
                return {}

    @staticmethod
    def set_cookie(cookie, value, time):
        from http import cookies
        c = cookies.SimpleCookie()
        # c=cookie.load(app.environ['HTTP_COOKIE'])
        directory = app.url['base_sub'] if app.front else app.url['admin_sub']
        c[cookie] = value
        c[cookie]["path"] = directory
        c[cookie]["expires"] = time
        c[cookie]["httponly"] = True
        functions.cookies.append(c[cookie].OutputString())
        return True

    @staticmethod
    def url_redirect(url):
        ruta = functions.generar_url(url)
        current = functions.current_url()
        if (ruta != current):
            return ruta
        else:
            return ""

    @staticmethod
    def get_idseccion(url: str):
        url = url.split('-', 2)
        try:
            return int(url[0])
        except Exception:
            return -1
        

    @staticmethod
    def url_seccion(url_base: list, seccion=dict, return_url=False, extra_variables=False):
        url = url_base
        extra = ""
        if 0 in seccion:
            extra += str(seccion[0])
            if 'url' in seccion:
                extra += "-" + seccion['url']
            elif 'titulo' in seccion:
                extra += "-" + functions.url_amigable(seccion['titulo'])

        url.append(extra)
        if return_url:
            return url
        else:
            return functions.generar_url(url, extra_variables)

    @staticmethod
    def generar_url(url, extra={}, front_auto=True, front=True):
        url = '/'.join(map(str, url))
        if isinstance(extra, dict) and len(extra) > 0:
            url = url+"?" + urlencode(extra, 'utf-8')
        else:
            if (len(app.get) > 0):
                if not isinstance(extra, bool) or extra == True:
                    url = url+"?" + urlencode(app.get, 'utf-8')

        url = (app.get_url() if front_auto else app.get_url(front)) + url
        return url

    @staticmethod
    def current_url():
        environ = app.environ
        url = environ['wsgi.url_scheme']+'://'
        if environ.get('HTTP_HOST'):
            url += environ['HTTP_HOST']
        else:
            url += environ['SERVER_NAME']

            if environ['wsgi.url_scheme'] == 'https':
                if environ['SERVER_PORT'] != '443':
                    url += ':' + environ['SERVER_PORT']
            else:
                if environ['SERVER_PORT'] != '80':
                    url += ':' + environ['SERVER_PORT']
        url += environ['SCRIPT_NAME']
        url += environ['PATH_INFO']
        if len(app.get) > 0:
            url += '?' + urlencode(app.get, 'utf-8')
        return url

    @staticmethod
    def generar_pass(length=8):
        import string
        import secrets
        password = ''.join(secrets.choice(
            string.ascii_uppercase + string.digits) for _ in range(length))
        return password

    @staticmethod
    def url_amigable(url=""):
        url = functions.replaceMultiple(
            url, ['á', 'à', 'â', 'ã', 'ª', 'ä'], 'a')
        url = functions.replaceMultiple(url, ['Á', 'À', 'Â', 'Ã', 'Ä'], "A")
        url = functions.replaceMultiple(url, ['Í', 'Ì', 'Î', 'Ï'], "I")
        url = functions.replaceMultiple(url, ['í', 'ì', 'î', 'ï'], "i")
        url = functions.replaceMultiple(url, ['é', 'è', 'ê', 'ë'], "e")
        url = functions.replaceMultiple(url, ['É', 'È', 'Ê', 'Ë'], "E")
        url = functions.replaceMultiple(url, ['ó', 'ò', 'ô', 'õ', 'ö'], "o")
        url = functions.replaceMultiple(url, ['Ó', 'Ò', 'Ô', 'Õ', 'Ö'], "O")
        url = functions.replaceMultiple(url, ['ú', 'ù', 'û', 'ü'], "u")
        url = functions.replaceMultiple(url, ['Ú', 'Ù', 'Û', 'Ü'], "U")
        url = functions.replaceMultiple(
            url, ['[', '^', '´', '`', '¨', '~', ']', ' ', '/', '°', 'º'], "-")
        url = url.replace("ç", "c")
        url = url.replace("Ç", "C")
        url = url.replace("ñ", "n")
        url = url.replace("Ñ", "N")
        url = url.replace("Ý", "Y")
        url = url.replace("ý", "y")
        url = url.lower()
        return url

    @staticmethod
    def replaceMultiple(mainString, toBeReplaces, newString):
        # Iterate over the strings to be replaced
        for elem in toBeReplaces:
            # Check if string is in the main string
            if elem in mainString:
                # Replace the string
                mainString = mainString.replace(elem, newString)
        return mainString

    @staticmethod
    def fecha_archivo(archivo, only_fecha=False, final_file=''):
        c = '?time=' if "?" not in archivo else '&time='
        ac = archivo.split('?', 2)[0]
        if final_file != '':
            archivo = final_file

        my_file = Path(ac)

        if only_fecha:
            return int(getmtime(ac)) if my_file.is_file() else -1
        else:
            return archivo + c + str(int(getmtime(ac))) if my_file.is_file() else ""

    @staticmethod
    def formato_precio(precio):
        final='${:,}'.format(precio)
        final=final.replace(',','.')
        #final='${.,0f}'.format(float(precio))
        return final

    @staticmethod
    def current_time(formato:str="%Y-%m-%d %H:%M:%S", as_string:bool=True):
        """ fecha actual en zona horaria santiago, formato opcional
        :type formato:str:
        :param formato:str:
    
        :type as_string:bool:
        :param as_string:bool:
    
        :raises:
    
        :rtype: datetime.timestamp() or str
        """

        import datetime
        import pytz
        fecha = datetime.datetime.now(pytz.timezone(functions.timezone))
        if as_string:
            return fecha.strftime(formato)
        else:
            return fecha.timestamp()

    @staticmethod
    def formato_fecha(fecha_string: str, formato='', original_format='', as_string=True):
        '''Fecha con formato opcional'''
        import datetime

        if formato == '':
            formato = '%d de %B del %Y'
        if original_format == '':
            original_format = "%Y-%m-%d %H:%M:%S"
        if not isinstance(fecha_string, str):
            fecha = datetime.datetime.fromtimestamp(fecha_string)
        else:
            fecha = datetime.datetime.strptime(fecha_string, original_format)
        if as_string:
            return fecha.strftime(formato)
        else:
            return fecha.timestamp()


        

    @staticmethod
    def getContrastColor(hexColor: str):
        # rgb
        hexColor = hexColor.lstrip('#')
        R1, G1, B1 = tuple(int(hexColor[i:i+2], 16) for i in (0, 2, 4))

        # black rgb
        blackColor = "#000000"
        blackColor = blackColor.lstrip('#')
        R2BlackColor, G2BlackColor, B2BlackColor = tuple(
            int(blackColor[i:i+2], 16) for i in (0, 2, 4))

        # contrast ratio
        L1 = 0.2126 * pow(R1 / 255, 2.2) + 0.7152 * \
            pow(G1 / 255, 2.2) + 0.0722 * pow(B1 / 255, 2.2)
        L2 = 0.2126 * pow(R2BlackColor / 255, 2.2) + 0.7152 * \
            pow(G2BlackColor / 255, 2.2) + 0.0722 * \
            pow(B2BlackColor / 255, 2.2)

        contrastRatio = 0
        if L1 > L2:
            contrastRatio = int((L1 + 0.05) / (L2 + 0.05))
        else:
            contrastRatio = int((L2 + 0.05) / (L1 + 0.05))

        # If contrast is more than 5, return black color
        if contrastRatio > 5:
            return '#000'
        else:
            # if not, return white color.
            return '#fff'

    @staticmethod
    def ruta(texto):
        texto = texto.strip()
        if "http" in texto or texto == '#':
            ruta = texto
        elif '.' == texto:
            ruta = ''
        else:
            ruta = "http://" + texto

        return ruta
        
    @staticmethod
    def active(string):
        pagina = app.environ["PATH_INFO"]
        url    = functions.current_url()
        if string in pagina:
            return True
        elif url == string:
            return True
        else:
            return False
        
    

    @staticmethod
    def crear_arbol(data: list, idpadre=0):
        tree = {'children': {}, 'root': {}}
        for node in data:
            id = int(node[0])
            node['idpadre'][0] = int(node['idpadre'][0])
            # Puede que exista el children creado si los hijos entran antes que el padre
            node['children'] = tree['children'][id]['children'] if id in tree['children'] else {}
            tree['children'][id] = node
            if int(node['idpadre'][0]) == idpadre:
                tree['root'][id] = tree['children'][id]
            else:
                tree['children'][node['idpadre'][0]
                                 ]['children'][id] = tree['children'][id]
        return tree['root']

    @staticmethod
    def file_size(file_url, only_size=False):
        from os import stat
        if not only_size:
            size = stat(file_url).st_size
        else:
            size = file_url

        unit = ['b', 'kb', 'mb', 'gb', 'tb', 'pb']
        for u in unit:
            if abs(size) < 1024.0:
                return "%3.2f %s" % (size, u)
            size /= 1024.0

        return "%.2f %s" % (size, 'Yb')

    @staticmethod
    def remove_tags(text):
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    @staticmethod
    def get_content_type_by_filename(file_name):
        from os.path import basename
        mime_type = ""
        mime_map = {}
        mime_map["js"] = "application/javascript"
        mime_map["xlsx"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        mime_map["xltx"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.template"
        mime_map["potx"] = "application/vnd.openxmlformats-officedocument.presentationml.template"
        mime_map["ppsx"] = "application/vnd.openxmlformats-officedocument.presentationml.slideshow"
        mime_map["pptx"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        mime_map["sldx"] = "application/vnd.openxmlformats-officedocument.presentationml.slide"
        mime_map["docx"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        mime_map["dotx"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.template"
        mime_map["xlam"] = "application/vnd.ms-excel.addin.macroEnabled.12"
        mime_map["xlsb"] = "application/vnd.ms-excel.sheet.binary.macroEnabled.12"
        mime_map["apk"] = "application/vnd.android.package-archive"
        try:
            suffix = ""
            name = basename(file_name)
            suffix = name.split('.')[-1]
            if suffix in mime_map.keys():
                mime_type = mime_map[suffix]
            else:
                import mimetypes
                mimetypes.init()
                mime_type = mimetypes.types_map["." + suffix]
        except Exception:
            mime_type = 'application/octet-stream'
        if not mime_type:
            mime_type = 'application/octet-stream'
        return mime_type
