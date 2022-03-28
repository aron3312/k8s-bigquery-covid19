from google.cloud import bigquery
import os
import json


if __name__ == '__main__':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/usr/src/app/key.json"
    client = bigquery.Client()
    all_query ="""
            SELECT * FROM `{}.{}.{}`
            """.format(
        client.project, "covid19", "hourly_report"
    )
    all_d = [dict(p) for p in client.query(all_query).result()]
    for d in all_d:
        for k in d:
            d[k] = str(d[k])
    with open('/usr/src/app/project/static/data/hourly_report.json', 'w', encoding='utf-8') as out:
        out.write(json.dumps(all_d, ensure_ascii=False))