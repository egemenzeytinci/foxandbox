from flask import Flask
from util.config import config
from util.ninja import Ninja

app = Flask('recommovie', template_folder='template', static_folder='./assets')

# update flask configuration
app.config['SECRET_KEY'] = config.app.secret_key

# update jinja environments
app.jinja_env.globals['f_minute'] = Ninja.format_minutes
app.jinja_env.globals['unescape'] = Ninja.unescape
