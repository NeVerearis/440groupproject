import os

from flask import current_app
from flask import Flask
from flask import g
from flask_login import LoginManager
from werkzeug.local import LocalProxy

from wiki.core import Wiki
from wiki.web.user import UserManager
# import wiki.web.routes

import unittest

class WikiError(Exception):
    pass

def get_wiki():
    wiki = getattr(g, '_wiki', None)
    if wiki is None:
        wiki = g._wiki = Wiki(current_app.config['CONTENT_DIR'])
    return wiki

current_wiki = LocalProxy(get_wiki)

def get_users():
    users = getattr(g, '_users', None)
    if users is None:
        users = g._users = UserManager(current_app.config['USER_DIR'])
    return users

current_users = LocalProxy(get_users)


def create_app(directory):
    app = Flask(__name__)
    app.config['CONTENT_DIR'] = directory
    app.config['TITLE'] = 'wiki'
    try:
        app.config.from_pyfile(
            os.path.join(app.config.get('CONTENT_DIR'), 'config.py')
        )
    except IOError:
        msg = "You need to place a config.py in your content directory."
        raise WikiError(msg)

    loginmanager.init_app(app)

    from wiki.web.routes import bp
    app.register_blueprint(bp)

    class TestAutocomplete(unittest.TestCase):

        def test_toa(self):
            with app.test_request_context():
                import wiki.web.routes
                self.assertEquals("<a href='/toast'>Toast</a>", routes.autocomplete("toa"))

        def test_noresult(self):
            with app.test_request_context():
                import wiki.web.routes
                self.assertEquals("", routes.autocomplete("toankal"))

        def test_home(self):
            with app.test_request_context():
                import wiki.web.routes
                self.assertEquals("<a href='/home'>test</a>", routes.autocomplete("test"))

    def suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestAutocomplete))
        return suite

    runner = unittest.TextTestRunner()
    runner.run(suite())

    return app


loginmanager = LoginManager()
loginmanager.login_view = 'wiki.user_login'

@loginmanager.user_loader
def load_user(name):
    return current_users.get_user(name)

