import os
import sqlite3
import datetime
from asyncore_wsgi import AsyncWebSocketHandler, make_server
import json


def application(environ, start_response):
    ret = "hello"
    with open("log.html", "r") as file:
        ret = file.read()
    ret = bytes(ret, "utf-8")
    start_response("200 OK", [("Content-Type", "text/html")])
    return [ret]


clients = []
file = os.path.join(os.path.dirname(__file__), "log.db")

if not os.path.exists(file):
    with open(file, "a+") as f:
        pass
    conn = sqlite3.connect(file)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS log ( id integer PRIMARY KEY AUTOINCREMENT, message text NOT NULL );"""
    )
    conn.commit()
    conn.close()


class SimpleChat(AsyncWebSocketHandler):
    lines = []
    conn = sqlite3.connect(file)
    cur = conn.cursor()

    def handleMessage(self):
        if self.data != "":
            try:
                data = json.loads(self.data)
                self.data = data
            except:
                pass
            message = {
                "type": "log",
                "time": datetime.datetime.now().time().strftime("%H:%M:%S"),
                "address": self.client_address[0],
                "data": self.data,
            }
            message = json.dumps(message)
            self.insert_bdd(message)
            for client in clients:
                if client != self:
                    self.send(client, message)

    def handleConnected(self):
        self.read(self)
        clients.append(self)
        msg = str(self.client_address) + " connected"
        self.insert_bdd(msg)

        for client in clients:
            message = {
                "type": "log",
                "time": datetime.datetime.now().time().strftime("%H:%M:%S"),
                "address": self.client_address[0],
                "data": "Connected",
            }
            message = json.dumps(message)
            self.send(client, message)

            self.send(
                client, json.dumps({"type": "connected", "data": str(len(clients))})
            )

    def handleClose(self):
        clients.remove(self)
        msg = str(self.client_address) + " closed"
        self.insert_bdd(msg)

        for client in clients:
            message = {
                "type": "log",
                "time": datetime.datetime.now().time().strftime("%H:%M:%S"),
                "address": self.client_address[0],
                "data": "Disconnected",
            }
            message = json.dumps(message)
            self.send(client, message)
            self.send(
                client, json.dumps({"type": "connected", "data": str(len(clients))})
            )

    def read(self, client):
        self.get_lines()
        for l in self.lines:
            client.sendMessage(l)
        client.sendMessage("END")

    def send(self, client, msg):
        self.get_lines()
        if msg != "":
            client.sendMessage(msg)

    def get_lines(self):
        if len(self.lines) == 0:
            self.cur.execute("SELECT message FROM log ORDER BY id DESC LIMIT 500")
            row = self.cur.fetchall()
            self.lines = list(reversed(list(l[0] for l in row)))

    def insert_bdd(self, msg):
        if msg != "":
            self.lines.append(msg)
            self.cur.execute("INSERT INTO log (message) VALUES (?)", (msg,))
            self.conn.commit()


port = 8001
httpd = make_server("", port, application, ws_handler_class=SimpleChat)
httpd.serve_forever()
