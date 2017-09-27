import os
from flask import url_for
from flask_script import Manager
from app import create_app, db
from app.models import Talk, User

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app)


if __name__ == '__main__':
    manager.run()
