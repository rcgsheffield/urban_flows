import logging.config

import flask

import settings

# Configure logging
logging.config.dictConfig(settings.LOGGING_CONFIG)


def create_app() -> flask.Flask:
    app = flask.Flask(__name__)

    # Register blueprints
    import blueprints.ott
    app.register_blueprint(blueprints.ott.blueprint)

    # Load response template
    with open(settings.RESPONSE_TEMPLATE_PATH) as file:
        app.config['RESPONSE_TEMPLATE'] = file.read()

    print('Initialised Flask application')

    return app
