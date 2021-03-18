from server import app
from web import home
from util.config import config

app.register_blueprint(home, url_prefix='/')

if __name__ == '__main__':
    port = config.app.port
    is_debug = config.app.debug
    app.run(host='0.0.0.0', port=port, debug=is_debug)
