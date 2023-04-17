#!flask/bin/python
from werkzeug.middleware.profiler import ProfilerMiddleware
# from kon import app
from flask import Flask
from ..config import Config
from flask_login import LoginManager
from ..app.routes import kon
from ..app.utils import *
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config.from_object(Config)
app.config['PROFILE'] = True
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30], profile_dir=dir_path)


# Used by flask_login to maintain the current user state
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    """Used by flask-login library to retrieve user's identification using its id

    """
    user = user_info_initialize(user_id)
    return user


login_manager.init_app(app)
login_manager.login_view = 'kon.login'

app.register_blueprint(kon, url_prefix='/')

if __name__ == "__main__":
    app.run(debug=True, port=5100)
