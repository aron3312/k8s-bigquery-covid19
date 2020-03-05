from config import *
from google.cloud import bigquery
import requests
import json
import os
from datetime import datetime

def get_latest_covid_data(client):
    table_id ="{}.{}.{}".format(client.project, dataset_name, table_name)
    table = client.get_table(table_id)

    req = requests.get("https://lab.isaaclin.cn/nCoV/api/area?latest=1")
    all_data = json.loads(req.content.decode('utf-8'))['results']
    need_data = []
    for d in all_data:
        if not d["cities"]:
            row = [d['countryName'], d['countryEnglishName'], d["provinceName"], d["provinceEnglishName"], "",
                   d["currentConfirmedCount"], d["confirmedCount"], d["suspectedCount"], d["curedCount"], d["deadCount"],
                   d["updateTime"]
                   ]
            row = [p if p else "" for p in row]
            need_data.append(tuple(row))
        else:
            row = [d['countryName'], d['countryEnglishName'], d["provinceName"], d["provinceEnglishName"], "",
                   d["currentConfirmedCount"], d["confirmedCount"], d["suspectedCount"], d["curedCount"], d["deadCount"],
                   d["updateTime"]
                   ]
            row = [p if p else "" for p in row]
            need_data.append(tuple(row))
            for city in d["cities"]:
                row = [d['countryName'], d['countryEnglishName'], d["provinceName"], d["provinceEnglishName"], city["cityName"],
                       city["currentConfirmedCount"], city["confirmedCount"], city["suspectedCount"], city["curedCount"],
                       city["deadCount"],
                       d["updateTime"]
                       ]
                row = [p if p else "" for p in row]
                need_data.append(tuple(row))
    client.insert_rows(table, need_data)
    print("Finish update data at {}".format(str(datetime.now())))
    return None


if __name__ == '__main__':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/usr/src/app/key.json"
    client = bigquery.Client()
    get_latest_covid_data(client)