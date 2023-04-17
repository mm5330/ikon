from flask import Flask
from config import Config
from flask_login import LoginManager
from app.routes import kon
from app.utils import *

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config.from_object(Config)

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
    app.run(port=5100)
