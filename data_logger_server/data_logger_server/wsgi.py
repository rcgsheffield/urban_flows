"""
WSGI entry point
https://flask.palletsprojects.com/en/2.0.x/deploying/wsgi-standalone/#uwsgi
"""

import app_factory

app = app_factory.create_app()
