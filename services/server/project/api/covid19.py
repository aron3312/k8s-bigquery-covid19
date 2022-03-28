import os
import pandas as pd
import json
from flask import Blueprint, jsonify, render_template,send_file, request
from project import client, location_map
from project.config import *
from opencc import OpenCC
import numpy as np

covid19_blueprint = Blueprint('covid19', __name__)
cc = OpenCC('s2t')


@covid19_blueprint.route('/', methods=['GET'])
def index():
    all_query ="""
            SELECT CAST(all_confirmed as int64) as all_confirmed, CAST(all_cured as int64) as all_cured, CAST(all_dead as int64) as all_dead,provinceName, updateTime, crawlTime,CAST(update_confirmed as int64) as update_confirmed,CAST(update_cured as int64) as update_cured,CAST(update_dead as int64) as update_dead FROM `{}.{}.{}` ORDER BY crawlTime DESC 
            """.format(
        client.project, dataset_name, "hourly_report"
    )
    all_d = [dict(p) for p in client.query(all_query).result()]
    update_time = all_d[0]['crawlTime']
    map_data = {"max": max([data["all_confirmed"] for data in all_d])}
    confirmed_mean = sum([p["all_confirmed"] for p in all_d])/len(all_d)
    map_data["data"] = [{"lat": location_map[p["provinceName"]][1], "lng":location_map[p["provinceName"]][0], "count":p["all_confirmed"], "name": cc.convert(p['provinceName']), "type": "red"} if p["all_confirmed"] > confirmed_mean else
                        {"lat": location_map[p["provinceName"]][1], "lng": location_map[p["provinceName"]][0],
                         "count": p["all_confirmed"], "name": cc.convert(p['provinceName']), "type": "green"}
                        for p in all_d if p["provinceName"] in location_map and location_map[p["provinceName"]]]
    return render_template("index.html",
                           table_data=all_d,
                           all_d=(sum([p['all_cured'] for p in all_d]), sum([p['all_confirmed'] for p in all_d]), sum([p['all_dead'] for p in all_d])),
                           map_data=json.dumps(map_data, ensure_ascii=False),
                           update_time=update_time
                           )


@covid19_blueprint.route('/area-chart', methods=['GET'])
def area_chart():
    query = """
    SELECT
      DISTINCT t.provinceName,
      t.confirmedCount,
      t.curedCount,
      t.deadCount,
      r.date
    FROM (
      SELECT
        DISTINCT DATE(TIMESTAMP_MILLIS(CAST(updateTime AS int64))) AS date,
        provinceName,
        MAX(updateTime) AS time
      FROM
        `speech-251314.covid19.covid_people_count`
      GROUP BY
        date,
        provinceName) r
    INNER JOIN
      `speech-251314.covid19.covid_people_count` t
    ON
      t.updateTime = r.time
      AND t.provinceName = r.provinceName
      AND DATE(TIMESTAMP_MILLIS(CAST(t.updateTime AS int64))) = r.date
    WHERE
      t.cityName = ""
    ORDER BY
  r.date
    """.format(client.project, dataset_name, table_name,client.project, dataset_name, table_name)
    all_d = pd.DataFrame([dict(p) for p in client.query(query).result()])
    area_list = ['台湾', '日本', '伊朗', '西班牙', '英国', '美国', '意大利', '湖北省']
    all_d = all_d[all_d["provinceName"].isin(area_list)]
    all_d["provinceName"] = [cc.convert(p) for p in list(all_d["provinceName"])]
    r = all_d.pivot(index="date", columns='provinceName', values=['confirmedCount', 'curedCount', 'deadCount'])
    r.columns = r.columns.map('_'.join)
    r['date'] = r.index
    r = r.fillna(method="ffill").fillna(method="bfill")
    r = list(r.T.to_dict().values())
    for p in r:
        p['date'] = str(p['date'])
    return render_template("area_chart.html", data=json.dumps(r, ensure_ascii=False))


@covid19_blueprint.route('/api/getlocation/<area_name>', methods=['GET'])
def get_location(area_name):
    all_query ="""
            SELECT * FROM `{}.{}.{}` WHERE provinceName = '{}' ORDER BY crawlTime DESC 
            """.format(
        client.project, dataset_name, "hourly_report",area_name
    )
    all_d = [dict(p) for p in client.query(all_query).result()][0]
    return jsonify(all_d)

@covid19_blueprint.route('/api/getlazy', methods=['GET'])
def get_lazy():
    page = request.args.get('start', default=0)
    length = request.args.get('length')
    if page and length:
        page = int(page)
        length = int(length)
        page = (page / length) + 1 if page > 0 else 1
        print(length)
        length_query = """SELECT COUNT(*)  FROM `{}.{}.{}` """.format(client.project, dataset_name, "hourly_report")
        d_len = [list(p) for p in client.query(length_query).result()][0]
        if page == 1:
            all_query = """
                        SELECT * FROM (SELECT ROW_NUMBER() OVER() row_number, * FROM `{}.{}.{}`  ORDER BY row_number) LIMIT {}
                        """.format(client.project, dataset_name, "hourly_report", length)
        else:
            all_query = """
                        SELECT * FROM (SELECT ROW_NUMBER() OVER() row_number, * FROM `{}.{}.{}`  ORDER BY row_number) WHERE row_number > {} LIMIT {}
                        """.format(client.project, dataset_name, "hourly_report", page * length, length)
        all_d = [dict(p) for p in client.query(all_query).result()]
        final_d = []
        for d in all_d:
            final_d.append([d['provinceName'],d['all_confirmed'], d['update_confirmed'], d['all_cured'], d['update_cured'], d['all_dead'], d['update_dead']])
        final = {"recordsTotal": d_len, "recordsFiltered": d_len,"data": final_d}
        return jsonify(final)
    else:
        return "參數錯誤"


@covid19_blueprint.route('/covid19/ping', methods=['GET'])
def ping():
    return jsonify({
        'status': 'success',
        'message': 'pong!',
        'container_id': os.uname()[1]
    })

# SSL

@covid19_blueprint.route('/.well-known/acme-challenge/LSwzUy9rQ9iLCswGwWf5SGagrUl6bW_u5BoJy6mNwfs', methods=['GET'])
def test1():
    return send_file('LSwzUy9rQ9iLCswGwWf5SGagrUl6bW_u5BoJy6mNwfs')


@covid19_blueprint.route('/.well-known/acme-challenge/vZcPP1Vh_4FiQXgl3lkAzC2tl_9dNKWuW5XhHb2MiY8', methods=['GET'])
def test2():
    return send_file('vZcPP1Vh_4FiQXgl3lkAzC2tl_9dNKWuW5XhHb2MiY8')

if __name__ == '__main__':
    app.run()
