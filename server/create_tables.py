from flask.ext.script import Manager
from server.models import db_config
import server

app = server.make_app()
manager = Manager(app, with_default_commands=False)


@manager.command
def init_db():
    db_config.init_db()

if __name__ == '__main__':
    manager.run()
