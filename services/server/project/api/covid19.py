import os
import pandas as pd
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
    cols = list(all_d[0].keys())
    all_df = pd.DataFrame([tuple(p.values()) for p in all_d], columns=cols)
    all_cured = all_df[(all_df["cityName"] == "") & (all_df["curedCount"] != "")].groupby("provinceName").apply(lambda x: x.sort_values(by='updateTime', ascending=False).iloc[0,:]["curedCount"]).astype(int).sum()
    all_infect = all_df[(all_df["cityName"] == "") & (all_df["confirmedCount"] != "")].groupby("provinceName").apply(lambda x: x.sort_values(by='updateTime', ascending=False).iloc[0,:]["confirmedCount"]).astype(int).sum()
    all_dead = all_df[(all_df["cityName"] == "") & (all_df["deadCount"] != "")].groupby("provinceName").apply(lambda x: x.sort_values(by='updateTime', ascending=False).iloc[0,:]["deadCount"]).astype(int).sum()
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
