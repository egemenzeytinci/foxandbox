from attrdict import AttrDict
from datetime import date
from db.factory import BasicFactory
from flask import Blueprint, render_template
from server import app

home = Blueprint('home', app.name)


@home.route('/', methods=['GET'])
def get_home():
    bf = BasicFactory()

    # get day number of today
    day = date.today().day

    # get 10 movies for the slider
    slides = bf.get_by_limit_and_offset(offset=day - 1)

    # get other 10 movies for the scrollable grid
    grid_movies = bf.get_by_limit_and_offset(offset=day)

    # get other 8 movies for the card items
    card_movies = bf.get_by_limit_and_offset(offset=day + 1, limit=8)

    r = AttrDict()

    r.slides = slides
    r.grid_movies = grid_movies
    r.card_movies = card_movies

    return render_template('home.html', **r)
