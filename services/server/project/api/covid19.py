import os
from flask import Blueprint, jsonify, render_template
from project import client
from project.config import *

covid19_blueprint = Blueprint('covid19', __name__)


@covid19_blueprint.route('/', methods=['GET'])
def index():
    all_query = """
    SELECT * FROM `{}.{}.{}`
    """.format(client.project, dataset_name, table_name)
    all_d = [p for p in client.query(all_query).result()]
    all_cured = sum([int(p["curedCount"]) for p in all_d if p["curedCount"] and not p["cityName"]])
    all_infect = sum([int(p["confirmedCount"]) for p in all_d if p["confirmedCount"] and not p["cityName"]])
    all_dead = sum([int(p["deadCount"]) for p in all_d if p["deadCount"] and not p["cityName"]])
    return render_template("index.html", all_d=(all_cured, all_infect, all_dead))

@covid19_blueprint.route('/covid19', methods=['GET'])
def list_all():
    query ="""
    SELECT * FROM `{}.{}.{}`;
    """.format(client.project, dataset_name, table_name)
    query_job = client.query(query)
    results = [dict(p.items()) for p in query_job]
    return jsonify(results)


@covid19_blueprint.route('/covid19/ping', methods=['GET'])
def ping():
    return jsonify({
        'status': 'success',
        'message': 'pong!',
        'container_id': os.uname()[1]
    })




if __name__ == '__main__':
    app.run()
