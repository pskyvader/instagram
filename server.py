from wsgiref.simple_server import make_server
import passenger_wsgi

port=80
srv = make_server('', port, passenger_wsgi.application)
print("En port {}... ctrl-c to quit server.".format(port))

try:
    srv.serve_forever()
except KeyboardInterrupt:
    srv.server_close()
    print("Server Stopped")
except:
    srv.server_close()
    print("Server Stopped")
