from google.cloud import bigquery

covid_data_schema = [
    bigquery.SchemaField("countryName", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("countryEnglishName", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("provinceName", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("provinceEnglishName", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("cityName", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("currentConfirmedCount", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("confirmedCount", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("suspectedCount", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("curedCount", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("deadCount", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("updateTime", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("crawlTime", "DATETIME	", mode="REQUIRED")
]

daily_report_schema = [
    bigquery.SchemaField("all_confirmed", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("all_cured", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("all_dead", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("provinceName", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("updateTime", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("crawlTime", "DATETIME", mode="REQUIRED"),
    bigquery.SchemaField("update_confirmed", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("update_cured", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("update_dead", "STRING", mode="REQUIRED"),

]