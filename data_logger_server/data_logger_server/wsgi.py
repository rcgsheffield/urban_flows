"""
WSGI entry point
"""

import app_factory

app = app_factory.create_app()

if __name__ == '__main__':
    app.run()
