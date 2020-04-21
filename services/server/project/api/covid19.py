import os
import pandas as pd
import json
from flask import Blueprint, jsonify, render_template,send_file
from project import client, location_map
from project.config import *
from opencc import OpenCC
import numpy as np

covid19_blueprint = Blueprint('covid19', __name__)
cc = OpenCC('s2t')
@covid19_blueprint.route('/', methods=['GET'])
def index():
    all_query ="""
            SELECT CAST(all_confirmed as int64) as all_confirmed, CAST(all_cured as int64) as all_cured, CAST(all_dead as int64) as all_dead,provinceName, updateTime, crawlTime FROM `{}.{}.{}` ORDER BY crawlTime DESC 
            """.format(
        client.project, dataset_name, "hourly_report"
    )
    all_d = [dict(p) for p in client.query(all_query).result()]
    now_history_data = pd.DataFrame([tuple(p.values()) for p in all_d], columns=list(all_d[0].keys()))
    compare_data = now_history_data.groupby(["provinceName"]).apply(lambda x: np.array(x.sort_values("crawlTime", ascending=False).iloc[0,:3].to_numpy()) - np.array(x.sort_values("crawlTime", ascending=False).iloc[1,:3].to_numpy()) if len(x) > 1 else "")
    compare_map = {name: list(value) for value, name in zip(list(compare_data), compare_data.index)}
    update_time = all_d[0]['crawlTime']
    all_d = [p for p in all_d if p['crawlTime'] == update_time]
    map_data = {"max": max([p["all_confirmed"] for p in all_d])}
    confirmed_mean = sum([p["all_confirmed"] for p in all_d])/len(all_d)
    map_data["data"] = [{"lat": location_map[p["provinceName"]][1], "lng":location_map[p["provinceName"]][0], "count":p["all_confirmed"], "name": cc.convert(p['provinceName']), "type": "red"} if p["all_confirmed"] > confirmed_mean else
                        {"lat": location_map[p["provinceName"]][1], "lng": location_map[p["provinceName"]][0],
                         "count": p["all_confirmed"], "name": cc.convert(p['provinceName']), "type": "green"}
                        for p in all_d if p["provinceName"] in location_map and location_map[p["provinceName"]]]
    for d in all_d:
        if d["provinceName"] in compare_map:
            d["update_data"] = compare_map[d["provinceName"]]
            d['provinceName'] = cc.convert(d['provinceName'])
        else:
            d["update_data"] = []
            d['provinceName'] = cc.convert(d['provinceName'])
    return render_template("index.html",
                           all_d=(sum([p['all_cured'] for p in all_d]), sum([p['all_confirmed'] for p in all_d]), sum([p['all_dead'] for p in all_d])),
                           map_data=json.dumps(map_data, ensure_ascii=False),
                           table_data=all_d,
                           update_time=update_time
                           )


@covid19_blueprint.route('/area-chart', methods=['GET'])
def area_chart():
    query ="""
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
