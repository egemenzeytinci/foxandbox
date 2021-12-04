from attrdict import AttrDict
from datetime import date
from db.factory import BasicFactory
from flask import Blueprint, render_template
from server import app
from validation.detail import DetailGetForm
from werkzeug.datastructures import MultiDict


home = Blueprint('home', app.name)


@home.get('/')
def get_home():
    """
    Get home page

    :rtype: flask.Response
    """
    bf = BasicFactory()

    # get day number of today
    day = date.today().day

    # get 10 movies for the slider
    slides = bf.get_by_limit_and_offset(offset=day - 1)

    # get other 10 movies for the scrollable grid
    grid_movies = bf.get_by_limit_and_offset(offset=day)

    # get other 8 movies for the card items
    card_movies = bf.get_new_released_movies()

    r = AttrDict()

    # set page parameters
    r.slides = slides
    r.grid_movies = grid_movies
    r.card_movies = card_movies

    return render_template('home.html', **r)


@home.get('/detail/<title_id>')
def get_detail(title_id):
    """
    Get detail page

    :rtype: flask.Response
    """
    # create form arguments
    args = MultiDict()
    args.add('title_id', title_id)

    form = DetailGetForm(args)

    # validate form
    if not form.validate():
        message = form.error()

        return render_template('error.html', message=message)

    bf = BasicFactory()

    # get base movie by title id
    original = bf.get_by_id(title_id)

    if original is None:
        message = 'The movie could not found.'

        return render_template('error.html', message=message)

    # get recommendations by base movie
    recommendations = bf.get_recommendations(
        title_id=title_id,
        title_type=original.basic.title_type,
        cluster=original.basic.cluster,
        genre=original.basic.genres
    )

    r = AttrDict()

    # set page parameters
    r.original = original
    r.recommendations = recommendations

    return render_template('detail.html', **r)
