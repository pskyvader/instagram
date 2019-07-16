from wsgiref.simple_server import make_server
import passenger_wsgi

srv = make_server('localhost', 80, passenger_wsgi.application)
print("En port 80... ctrl-c to quit server.")

try:
    srv.serve_forever()
except KeyboardInterrupt:
    srv.server_close()
    print("Server Stopped")
except:
    srv.server_close()
    print("Server Stopped")
