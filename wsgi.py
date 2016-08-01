import server


class ClientProxy(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ["wsgi.url_scheme"] = server.app.config['URL_SCHEME']
        environ["HTTP_HOST"] = server.app.config['SERVER_URL']
        return self.app(environ, start_response)

application = server.init(server.make_app())
application = server.init_web(application)
application.wsgi_app = ClientProxy(application.wsgi_app)

if __name__ == '__main__':

    application.run('0.0.0.0', 9090, use_debugger=True, use_reloader=True)
