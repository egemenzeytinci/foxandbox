from attrdict import AttrDict
from db.service import BasicService
from elastic.service import ElasticBasicService
from flask import Blueprint, render_template
from server import app
from server.message import Message
from validation.movie import MovieListForm

movie = Blueprint('movie', app.name)


@movie.post('/search')
def search():
    """
    Search on the elasticsearch index

    :rtype: flask.Response
    """
    m = Message()

    ebs = ElasticBasicService()

    form = MovieListForm()

    # validate form
    if not form.validate():
        m.message = form.error()

        return m.json()

    # search by filters
    result = ebs.search(
        genres=form.genres.data,
        years=form.years.data,
        score=form.score.data,
        num_votes=form.num_votes.data,
        page=form.page.data,
        exact=form.exact.data
    )

    m.status = True

    m.total_count = result.total_count
    m.results = result.hits

    return m.json()


@movie.get('/')
def get_home():
    """
    Get movie home page

    :rtype: flask.Response
    """
    r = AttrDict()

    bs = BasicService()

    # all genres for filter
    r.genres = [g[0] for g in bs.get_genres()]

    # get default movies to list
    r.movies = bs.get_most_popular_items(limit=12)

    return render_template('movie.html', **r)
