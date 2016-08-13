from server.config import BaseConfig, _base


class LocalConfig(BaseConfig):
    ENV = 'local'
    GOOGLE_CALLBACK_URL = 'http://localhost:5000/login/oauth2callback'
    STATIC_FOLDER = BaseConfig.BASE_DIR + '/client/static/'
    CLIENT_SECRET = BaseConfig.BASE_DIR + '/auth/google/client_secret_local.json'
    SERVER_URL = 'localhost:5000'
