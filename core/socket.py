from websocket import create_connection
import json


class socket:
    sock = None
    host = "ws://socket.mysitio.cl:8000/ws"
    url="http://socket.mysitio.cl/"
    intento=False

    @staticmethod
    def send(msg):
        down=socket.download(socket.url+"port.txt")
        try:
            if socket.sock==None:
                down=socket.download(socket.url+"port.txt")
                socket.host=json.loads(down)['final_url']
                socket.sock = create_connection(socket.host)
            socket.sock.send(msg)
        except Exception as e:
            print("error:",e)
            socket.sock=None
            if not socket.intento:
                socket.intento=True
                socket.create()


    @staticmethod
    def create():
        import urllib.request
        url=socket.url
        try:
            response = urllib.request.urlopen(url,timeout=1)
        except:
            pass

    @staticmethod
    def close():
        if socket.sock!=None:
            socket.sock.close()
            socket.sock=None

    @staticmethod
    def download(url):
        import urllib.request
        try:
            response =  urllib.request.urlopen(url)
            return response.read().decode('utf-8')
        except:
            return 'Error al obtener el archivo '+url+'. Intenta mas tarde'
        return True

