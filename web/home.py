from flask import Blueprint, render_template
from server import app

home = Blueprint('home', app.name)


@home.route('/', methods=['GET'])
def get_home():
    return render_template('home.html')
