import os
import json
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

# instantiate the extensions
client = bigquery.Client()
location_map = json.load(open("location_map.json", 'r', encoding='utf-8'))

def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    # enable CORS
    CORS(app)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)
    # app.config['TEMPLATES_AUTO_RELOAD'] = True

    # register blueprints
    from project.api.covid19 import covid19_blueprint
    from project.api.animal_cross import animal_cross_blueprint
    app.register_blueprint(covid19_blueprint)
    app.register_blueprint(animal_cross_blueprint)
    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app
