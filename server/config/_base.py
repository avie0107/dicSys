from os import path


def get_key(key_file):
    """
    keyをファイルから取得
    :param key_file:
    :return _key:
    """
    with open(key_file, 'r') as file:
        _key = file.read().rstrip()

    return _key


class BaseConfig:
    sample_key = 'sample'
    BASE_DIR = path.abspath(path.join(path.dirname(__file__), '../..'))
    SECRET_KEY = get_key(BASE_DIR+'/auth/flask/secret_key')
    URL_SCHEME = 'http'
