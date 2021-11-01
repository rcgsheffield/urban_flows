import flask

import settings


def create_app() -> flask.Flask:
    app = flask.Flask(__name__)

    # Load response template
    with open(settings.RESPONSE_TEMPLATE_PATH) as file:
        app.config['RESPONSE_TEMPLATE'] = file.read()

    return app
