import sys
import os
from core.app import app
import pprint
from beaker.middleware import SessionMiddleware



import sqlite3
import datetime
from asyncore_wsgi import AsyncWebSocketHandler, make_server
import json


sys.path.insert(0, os.path.dirname(__file__))


def application2(environ, start_response):
    # from datetime import datetime
    # init_time = datetime.now()

    app_web = app(os.path.dirname(__file__))
    main_data = app_web.init(environ)
    ret = main_data["response_body"]

    if isinstance(ret, str):
        if ret != "":
            ret = bytes(ret, "utf-8")
            from gzip import compress
            ret = compress(ret)
            main_data["headers"].append(("Accept-encoding", "gzip,deflate"))
            main_data["headers"].append(("Content-Encoding", "gzip"))
        else:
            ret = b""

    start_response(main_data["status"], main_data["headers"])
    # if main_data['status']=='200 OK':
    # print(environ['PATH_INFO'],'total', (datetime.now()-init_time).total_seconds()*1000)

    if "is_file" in main_data and main_data["is_file"]:
        f = open(main_data["file"], "rb")
        if "wsgi.file_wrapper" in environ:
            return environ["wsgi.file_wrapper"](f, 1024)
        else:
            # print('no filewrapper')
            return file_wrapper(f, 1024)
    else:
        return [ret]


def file_wrapper(fileobj, block_size=1024):
    try:
        data = fileobj.read(block_size)
        while data:
            yield data
            data = fileobj.read(block_size)
    finally:
        fileobj.close()


class LoggingMiddleware:
    def __init__(self, application):
        self.__application = application

    def __call__(self, environ, start_response):
        errors = environ["wsgi.errors"]

        def _start_response(status, headers, *args):
            if status != "200 OK":
                # pprint.pprint(('REQUEST', environ), stream=errors)
                pprint.pprint(("REQUEST:", environ["PATH_INFO"]), stream=errors)
                # pprint.pprint(('RESPONSE', status, headers), stream=errors)
                pprint.pprint(("RESPONSE:", status), stream=errors)
            return start_response(status, headers, *args)

        return self.__application(environ, _start_response)


session_opts = {
    "session.type": "file",
    "session.data_dir": "./session_data",
    "session.auto": True,
}

app2 = LoggingMiddleware(application2)
application = SessionMiddleware(app2, session_opts)






















clients = []
file=os.path.join(os.path.dirname(__file__),'log.db')

if not os.path.exists(file):
    with open(file,'a+') as f:
        pass
    conn = sqlite3.connect(file)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS log ( id integer PRIMARY KEY AUTOINCREMENT, message text NOT NULL );''')
    conn.commit()
    conn.close()


class SimpleChat(AsyncWebSocketHandler):
    lines=[]
    conn = sqlite3.connect(file)
    cur = conn.cursor()
    def handleMessage(self):
        if self.data!='':
            message='log: {} - {} - {} '.format(datetime.datetime.now().time(),self.client_address[0],self.data)
            self.insert_bdd(message)
            for client in clients:
                if client != self:
                    self.send(client,message)

    def handleConnected(self):
        #logging.info('new connection {}'.format(self))
        self.read(self)
        clients.append(self)
        msg=str(self.client_address)+" connected"
        self.insert_bdd(msg)

        for client in clients:
            message='log: {} - {} - {} '.format(datetime.datetime.now().time(),self.client_address[0]," - connected")
            self.send(client,message)
            self.send(client,"connected:" + str(len(clients)))
        
        

    def handleClose(self):
        clients.remove(self)
        msg=str(self.client_address)+" closed"
        self.insert_bdd(msg)

        for client in clients:
            message='log: {} - {} - {} '.format(datetime.datetime.now().time(),self.client_address[0]," - disconnected")
            self.send(client,message)
            self.send(client,"connected:" + str(len(clients)))

    def read(self,client):
        self.get_lines()
        for l in self.lines:
            client.sendMessage(l)
        client.sendMessage('END')

    def send(self,client,msg):
        self.get_lines()
        if msg!='':
            client.sendMessage(msg)
        

    def get_lines(self):
        if len(self.lines)==0:
            self.cur.execute("SELECT message FROM log ORDER BY id DESC LIMIT 500")
            row=self.cur.fetchall()
            self.lines = list(reversed(list(l[0] for l in row)))
    
    def insert_bdd(self,msg):
        if msg!='':
            self.lines.append(msg)
            self.cur.execute( "INSERT INTO log (message) VALUES (?)", (msg,) )
            self.conn.commit()
    



served=False
while not served:
    #port=random.randint(2000,20000)
    port=8080
    #logging.info('start make server. port {}'.format(port))
    try:
        httpd = make_server("", port, application, ws_handler_class=SimpleChat)
        served=True
        #logging.info('server connected. port {}'.format(port))
    except OSError as e:
        served=False
        #logging.info('error make server {}'.format(e))

with open('port.txt','w+') as f:
    final_url={'final_url':"ws://socket.mysitio.cl:"+str(port)+"/ws"}
    #logging.info('final url {}'.format(final_url))
    f.write(json.dumps(final_url))

httpd.serve_forever()