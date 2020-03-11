import os
import pandas as pd
import json
from flask import Blueprint, jsonify, render_template
from project import client
from project.config import *

covid19_blueprint = Blueprint('covid19', __name__)
# location_map = json.loads(open("location_map.json", 'r', encoding='utf-8'))

@covid19_blueprint.route('/', methods=['GET'])
def index():
    all_query = """
    SELECT sum(g.all_cured) as all_cured, sum(g.all_confirmed) as all_confirmed, sum(g.all_dead) as all_dead FROM (SELECT DISTINCT t.provinceName, t.updateTime, CAST(CASE WHEN t.curedCount = "" 
                THEN "0"
                ELSE t.curedCount
           END  as int64) as all_cured,
           CAST(CASE WHEN t.confirmedCount = "" 
                THEN "0"
                ELSE t.confirmedCount
           END  as int64) as all_confirmed,
           CAST(CASE WHEN t.deadCount = "" 
                THEN "0"
                ELSE t.deadCount
           END  as int64) as all_dead
           FROM 
(SELECT  provinceName, MAX(updateTime)  AS time,  FROM `{}.{}.{}` GROUP BY provinceName 
           )  r
           INNER JOIN `{}.{}.{}` t
ON t.provinceName = r.provinceName AND t.updateTime = r.time WHERE 　t.cityName = "")g
    """.format(client.project, dataset_name, table_name,client.project, dataset_name, table_name)
    all_d = [p for p in client.query(all_query).result()][0]

    # map_data = {"max": all_area_data.max()}
    # map_data["data"] = [p for p in all_area_data.index]

    return render_template("index.html", all_d=(all_d['all_cured'], all_d["all_confirmed"], all_d["all_dead"]))

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
