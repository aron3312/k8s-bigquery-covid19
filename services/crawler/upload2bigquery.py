from config import *
from google.cloud import bigquery
from crawler import Crawler
from opencc import OpenCC
import requests
import json
import os
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta


def get_latest_covid_data(client):
    cc = OpenCC('s2t')
    time = datetime.now() + timedelta(hours=8)
    table_id ="{}.{}.{}".format(client.project, dataset_name, table_name)
    table = client.get_table(table_id)
    req = requests.get("https://lab.isaaclin.cn/nCoV/api/area?latest=1")
    all_data = json.loads(req.content.decode('utf-8'))['results']
    need_data = []
    for d in all_data:
        if not d["cities"]:
            if d["provinceName"] == "台湾":
                d['countryName'] = "台湾"
                d['countryEnglishName'] = "Taiwan"
            row = [d['countryName'], d['countryEnglishName'], d["provinceName"], d["provinceEnglishName"], "",
                   d["currentConfirmedCount"], d["confirmedCount"], d["suspectedCount"], d["curedCount"], d["deadCount"],
                   d["updateTime"], time
                   ]
            row = [p if p else "" for p in row]
            need_data.append(tuple(row))
        else:
            row = [d['countryName'], d['countryEnglishName'], d["provinceName"], d["provinceEnglishName"], "",
                   d["currentConfirmedCount"], d["confirmedCount"], d["suspectedCount"], d["curedCount"], d["deadCount"],
                   d["updateTime"], time
                   ]
            row = [p if p else "" for p in row]
            need_data.append(tuple(row))
            for city in d["cities"]:
                row = [d['countryName'], d['countryEnglishName'], d["provinceName"], d["provinceEnglishName"], city["cityName"],
                       city["currentConfirmedCount"], city["confirmedCount"], city["suspectedCount"], city["curedCount"],
                       city["deadCount"],
                       d["updateTime"], time
                       ]
                row = [p if p else "" for p in row]
                need_data.append(tuple(row))
    client.insert_rows(table, need_data)
    print("Finish update data at {}".format(str(datetime.now())))
    all_query = """
    SELECT CAST(CASE WHEN confirmedCount = ""
                    THEN "0"
                    ELSE confirmedCount
               END  as int64) as all_confirmed,CAST(CASE WHEN curedCount = ""
                    THEN "0"
                    ELSE curedCount
               END  as int64) as all_cured,CAST(CASE WHEN deadCount = ""
                    THEN "0"
                    ELSE deadCount
               END  as int64) as all_dead, provinceName, updateTime, crawlTime FROM `{}.{}.{}` WHERE crawlTime  IN ((SELECT distinct crawlTime  FROM `{}.{}.{}` ORDER BY crawlTime DESC LIMIT 2)) AND cityNAME = "" AND provinceName != "中国" ORDER BY crawlTime DESC 
        """.format(
        client.project, dataset_name, table_name, client.project, dataset_name, table_name
    )
    all_d = [dict(p) for p in client.query(all_query).result()]
    now_history_data = pd.DataFrame([tuple(p.values()) for p in all_d], columns=list(all_d[0].keys()))
    compare_data = now_history_data.groupby(["provinceName"]).apply(
        lambda x: np.array(x.sort_values("crawlTime", ascending=False).iloc[0, :3].to_numpy()) - np.array(
            x.sort_values("crawlTime", ascending=False).iloc[1, :3].to_numpy()) if len(x) > 1 else "")
    compare_map = {name: list(value) for value, name in zip(list(compare_data), compare_data.index)}
    update_time = all_d[0]['crawlTime']
    all_d = [p for p in all_d if p['crawlTime'] == update_time]
    for d in all_d:
        if d["provinceName"] in compare_map:
            if len(compare_map[d["provinceName"]]) == 3:
                d["update_confirmed"] = compare_map[d["provinceName"]][0]
                d["update_coured"] = compare_map[d["provinceName"]][1]
                d["update_dead"] = compare_map[d["provinceName"]][2]
                d['provinceName'] = cc.convert(d['provinceName'])
            else:
                d["update_confirmed"] = 0
                d["update_coured"] = 0
                d["update_dead"] = 0
                d['provinceName'] = cc.convert(d['provinceName'])
        else:
            d["update_confirmed"] = ''
            d["update_coured"] = ''
            d["update_dead"] = ''
            d['provinceName'] = cc.convert(d['provinceName'])
    all_d = [tuple(p.values()) for p in all_d]
    delete = client.query("""
                 DELETE FROM `{}.{}.{}` WHERE TRUE
                 """.format(client.project, dataset_name, "hourly_report")
                 )
    print(delete.result())
    client.query("""
    INSERT `{}.{}.{}` (all_confirmed, all_cured, all_dead,provinceName, updateTime, crawlTime, update_confirmed, update_cured, update_dead) VALUES {}
    """.format(client.project, dataset_name, "hourly_report", ','.join(['('+','.join(['"' + str(a) + '"' for a in p]) + ')' for p in all_d]))).result()
    return None


if __name__ == '__main__':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/usr/src/app/key.json"
    client = bigquery.Client()
    try:
        get_latest_covid_data(client)
    except:
        crawler = Crawler()
        crawler.run(client, dataset_name, table_name)
