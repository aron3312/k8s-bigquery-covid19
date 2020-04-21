"""
@ProjectName: DXY-2019-nCov-Crawler
@FileName: crawler.py
@Author: Jiabao Lin
@Date: 2020/1/21
"""
from bs4 import BeautifulSoup
from userAgent import user_agent_list
from nameMap import country_type_map, city_name_map, country_name_map, continent_name_map
from datetime import datetime, timedelta
import re
import json
import time
import random
import logging
import requests


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class Crawler:
    def __init__(self):
        self.session = requests.session()
        # self.db = DB()
        self.crawl_timestamp = int()

    def run(self, client, dataset_name, table_name):
        self.crawler(client, dataset_name, table_name)

    def crawler(self,client, dataset_name, table_name):
        crawl_now_time = datetime.now() + timedelta(hours=8)
        table_id = "{}.{}.{}".format(client.project, dataset_name, table_name)
        table = client.get_table(table_id)
        self.session.headers.update(
            {
                'user-agent': random.choice(user_agent_list)
            }
        )
        self.crawl_timestamp = int(time.time() * 1000)
        try:
            r = self.session.get(url='https://ncov.dxy.cn/ncovh5/view/pneumonia')
        except requests.exceptions.ChunkedEncodingError:
            pass
        soup = BeautifulSoup(r.content, 'lxml')
        abroad_information = re.search(r'\[(.*)\]',
                                       str(soup.find('script', attrs={'id': 'getListByCountryTypeService2true'})))
        if abroad_information:
            temp = self.abroad_parser(abroad_information=abroad_information)
        area_information = re.search(r'\[(.*)\]', str(soup.find('script', attrs={'id': 'getAreaStat'})))
        if area_information:
            all_data = self.area_parser(area_information=area_information, temp=temp)
        need_data = []
        for d in all_data:
            if "cities" not in d:
                if d["provinceName"] == "台湾":
                    d['countryName'] = "台湾"
                    d['countryEnglishName'] = "Taiwan"
                row = [d['countryName'], d['countryEnglishName'], d["provinceName"], d["provinceEnglishName"], "",
                       d["currentConfirmedCount"], d["confirmedCount"], d["suspectedCount"], d["curedCount"],
                       d["deadCount"],
                       d["updateTime"], crawl_now_time
                       ]
                row = [p if p else "" for p in row]
                need_data.append(tuple(row))
            else:
                row = [d['countryName'], d['countryEnglishName'], d["provinceName"], d["provinceEnglishName"], "",
                       d["currentConfirmedCount"], d["confirmedCount"], d["suspectedCount"], d["curedCount"],
                       d["deadCount"],
                       d["updateTime"], crawl_now_time
                       ]
                row = [p if p else "" for p in row]
                need_data.append(tuple(row))
                for city in d["cities"]:
                    row = [d['countryName'], d['countryEnglishName'], d["provinceName"], d["provinceEnglishName"],
                           city["cityName"],
                           city["currentConfirmedCount"], city["confirmedCount"], city["suspectedCount"],
                           city["curedCount"],
                           city["deadCount"],
                           d["updateTime"], crawl_now_time
                           ]
                    row = [p if p else "" for p in row]
                    need_data.append(tuple(row))
        client.insert_rows(table, need_data)
        print("Finish update data at {}".format(str(datetime.now())))
        return None

    def area_parser(self, area_information, temp):
        area_information = json.loads(area_information.group(0))
        for area in area_information:
            area['comment'] = area['comment'].replace(' ', '')

            # Because the cities are given other attributes,
            # this part should not be used when checking the identical document.
            cities_backup = area.pop('cities')

            # If this document is not in current database, insert this attribute back to the document.
            area['cities'] = cities_backup

            area['countryName'] = '中国'
            area['countryEnglishName'] = 'China'
            area['continentName'] = '亚洲'
            area['continentEnglishName'] = 'Asia'
            area['provinceEnglishName'] = city_name_map[area['provinceShortName']]['engName']

            for city in area['cities']:
                if city['cityName'] != '待明确地区':
                    try:
                        city['cityEnglishName'] = city_name_map[area['provinceShortName']]['cities'][city['cityName']]
                    except KeyError:
                        print(area['provinceShortName'], city['cityName'])
                        pass
                else:
                    city['cityEnglishName'] = 'Area not defined'

            area['updateTime'] = self.crawl_timestamp
            temp.append(area)
        return temp

    def abroad_parser(self, abroad_information):
        countries = json.loads(abroad_information.group(0))
        all_country = []
        for country in countries:
            try:
                country.pop('id')
                country.pop('tags')
                country.pop('sort')
                # Ding Xiang Yuan have a large number of duplicates,
                # values are all the same, but the modifyTime are different.
                # I suppose the modifyTime is modification time for all documents, other than for only this document.
                # So this field will be popped out.
                country.pop('modifyTime')
                # createTime is also different even if the values are same.
                # Originally, the createTime represent the first diagnosis of the virus in this area,
                # but it seems different for abroad information.
                country.pop('createTime')
                country['comment'] = country['comment'].replace(' ', '')
            except KeyError:
                pass
            country.pop('countryType')
            country.pop('provinceId')
            country.pop('cityName')
            # The original provinceShortName are blank string
            country.pop('provinceShortName')
            # Rename the key continents to continentName
            country['continentName'] = country.pop('continents')

            # if self.db.find_one(collection='DXYArea', data=country):
            #     continue

            country['countryName'] = country.get('provinceName')
            country['provinceShortName'] = country.get('provinceName')
            country['continentEnglishName'] = continent_name_map.get(country['continentName'])
            country['countryEnglishName'] = country_name_map.get(country['countryName'])
            country['provinceEnglishName'] = country_name_map.get(country['countryName'])

            country['updateTime'] = self.crawl_timestamp
            all_country.append(country)
        return all_country


if __name__ == '__main__':
    crawler = Crawler()
    crawler.run()