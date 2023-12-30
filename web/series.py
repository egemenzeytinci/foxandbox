from addict import Dict
from db.model import ImageStatus
from db.service import BasicService
from elastic.service import ElasticBasicService
from flask import Blueprint, render_template
from server import app
from server.message import Message
from validation.title import TitleListForm

series = Blueprint('series', app.name)


@series.post('/search')
def search():
    """
    Search on the elasticsearch index

    :rtype: flask.Response
    """
    m = Message()

    ebs = ElasticBasicService()

    form = TitleListForm()

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
        exact=form.exact.data,
        type=form.type.data
    )

    m.status = True

    m.total_count = result.total_count
    m.results = result.hits

    return m.json()


@series.get('/')
def get_home():
    """
    Get series home page

    :rtype: flask.Response
    """
    r = Dict()

    bs = BasicService()

    # all genres for filter
    r.genres = [g[0] for g in bs.get_genres()]

    # get default movies to list
    r.movies = bs.get_most_popular_items(
        limit=12,
        type='series',
        img_status=ImageStatus.VERTICAL_IMAGE
    )

    return render_template('series.html', **r)
