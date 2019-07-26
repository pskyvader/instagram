from websocket import create_connection
import json


class socket:
    sock = None
    host = "ws://socket.mysitio.cl:8000/ws"
    url = "http://socket.mysitio.cl/"
    intento = False

    @staticmethod
    def send(msg):
        socket.create()
        if socket.sock != None:
            socket.sock.send(msg)

    @staticmethod
    def receive():
        socket.create()
        msg=''
        if socket.sock != None:
            msg=socket.sock.recv()
        return msg



    @staticmethod
    def create():
        import urllib.request

        if socket.sock != None:
            return

        url = socket.url
        try:
            if socket.intento:
                response = urllib.request.urlopen(url, timeout=1)
            down = socket.download(socket.url + "port.txt")
            socket.host = json.loads(down)["final_url"]
            socket.sock = create_connection(socket.host)
        except Exception as e:
            print("error:", e)
            socket.sock = None
            if not socket.intento:
                socket.intento = True
                socket.create()

    @staticmethod
    def close():
        if socket.sock != None:
            socket.sock.close()
            socket.sock = None

    @staticmethod
    def download(url):
        import urllib.request

        try:
            response = urllib.request.urlopen(url)
            return response.read().decode("utf-8")
        except:
            return "Error al obtener el archivo " + url + ". Intenta mas tarde"
        return True

