import json
from oauth2client.client import OAuth2WebServerFlow


class GoogleAuth:

    def __init__(self):
        self.flow = None
        self.client_data = None
        self.authorize_by_flow = None
        self.created_credentials = None
        self.email = None
        self.loaded_credentials = None
        self.valid_email = False

        self.scope = "https://www.googleapis.com/auth/userinfo.email"

    def config(self, client_json, redirect_url, logger):
        global _client_json_path, _logger, _redirect_url
        _client_json_path = client_json
        _logger = logger
        _redirect_url = redirect_url

    def load_client_data(self):
        with open(_client_json_path) as fio:
            client_json = json.load(fio)

        self.client_data = dict(client_id=client_json['web']['client_id'],
                                client_secret=client_json['web']['client_secret'])
        return self.client_data

    def make_flow(self, **kwargs):
        client_data = self.load_client_data()
        self.flow = OAuth2WebServerFlow(client_id=client_data['client_id'],
                                        client_secret=client_data['client_secret'],
                                        scope=self.scope,
                                        redirect_uri=_redirect_url,
                                        user_agent='kmsreact',
                                        **kwargs)
        return self.flow

    def authorized_url(self):
        flow = self.make_flow(access_type='offline', approval_prompt='force')
        self.authorize_by_flow = flow.step1_get_authorize_url()
        return self.authorize_by_flow

    def create_credentials(self, code):
        flow = self.make_flow(grant_type='authorization_code')
        self.created_credentials = flow.step2_exchange(code)

        return self.created_credentials

    def get_email(self, credentials):
        self.email = credentials.id_token['email']
        return self.email

    def validate_email(self, email):
        host = email.split('@')[1]
        if host == 'klab.com':
            self.valid_email = True

        return self.valid_email
