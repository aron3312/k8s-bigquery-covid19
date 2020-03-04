import os
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

# instantiate the extensions
client = bigquery.Client()


def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)

    # enable CORS
    CORS(app)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)


    # register blueprints
    from project.api.covid19 import covid19_blueprint
    app.register_blueprint(covid19_blueprint)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app
