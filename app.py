from server import app
from web import home, movie
from util.config import config

app.register_blueprint(home, url_prefix='/')
app.register_blueprint(movie, url_prefix='/movie')

if __name__ == '__main__':
    port = config.app.port
    is_debug = config.app.debug

    app.run(host='0.0.0.0', port=port, debug=is_debug)
