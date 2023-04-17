from flask import Flask
from config import Config
from app.routes import kon
from app import login_manager

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config.from_object(Config)

# Used by flask_login to maintain the current user state
login_manager.init_app(app)
login_manager.login_view = 'kon.login'

app.register_blueprint(kon, url_prefix='/')

if __name__ == "__main__":
    app.run(port=5100)
