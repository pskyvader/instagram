import sys
import os
from core.app import app
import pprint
from beaker.middleware import SessionMiddleware

sys.path.insert(0, os.path.dirname(__file__))


def application2(environ, start_response):
    #from datetime import datetime
    #init_time = datetime.now()

    app_web = app(os.path.dirname(__file__))
    main_data = app_web.init(environ)
    ret = main_data['response_body']

    if isinstance(ret, str) and ret != '':
        ret = bytes(ret, 'utf-8')
        from gzip import compress
        ret = compress(ret)
        main_data['headers'].append(('Accept-encoding', 'gzip,deflate'))
        main_data['headers'].append(('Content-Encoding', 'gzip'))
    print(main_data)
    start_response(main_data['status'], main_data['headers'])
    # if main_data['status']=='200 OK':
    #print(environ['PATH_INFO'],'total', (datetime.now()-init_time).total_seconds()*1000)

    if 'is_file' in main_data and main_data['is_file']:
        f = open(main_data['file'], 'rb')
        if 'wsgi.file_wrapper' in environ:
            return environ['wsgi.file_wrapper'](f, 1024)
        else:
            #print('no filewrapper')
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
        errors = environ['wsgi.errors']

        def _start_response(status, headers, *args):
            if status != "200 OK":
                #pprint.pprint(('REQUEST', environ), stream=errors)
                pprint.pprint(
                    ('REQUEST:', environ['PATH_INFO']), stream=errors)
                #pprint.pprint(('RESPONSE', status, headers), stream=errors)
                pprint.pprint(('RESPONSE:', status), stream=errors)
            return start_response(status, headers, *args)
        return self.__application(environ, _start_response)


session_opts = {
    'session.type': 'file',
    'session.data_dir': './session_data',
    'session.auto': True
}

app2 = LoggingMiddleware(application2)
application = SessionMiddleware(app2, session_opts)