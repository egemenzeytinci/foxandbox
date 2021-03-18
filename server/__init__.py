from flask import Flask
from util.config import config

app = Flask('recommovie', template_folder='template', static_folder='./assets')
app.config['SECRET_KEY'] = config.app.secret_key
