from config import *
from google.cloud import bigquery
from crawler import Crawler
import requests
import json
import os
from datetime import datetime
from datetime import timedelta

def get_latest_covid_data(client):
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
    all_d = [tuple(p) for p in client.query(all_query).result()]
    delete = client.query("""
                 DELETE FROM `{}.{}.{}` WHERE TRUE
                 """.format(client.project, dataset_name, "hourly_report")
                 )
    print(delete.result())
    client.query("""
    INSERT `{}.{}.{}` (all_confirmed, all_cured, all_dead, provinceName, updateTime, crawlTime) VALUES {}
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
