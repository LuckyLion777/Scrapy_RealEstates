# -*- coding: utf-8 -*-
import scrapy
import re
import json
import eviltransform

from real_estate_scraper.items import Fangtem


class FangSHSpider(scrapy.Spider):
    name = 'fang_sh'
    allowed_domains = ['fang.com']
    start_urls = [
        'https://sh.esf.fang.com/housing/__0_0_0_10000_1_0_0_0/',
        'https://sh.esf.fang.com/housing/__0_0_10000_20000_1_0_0_0/',
        'https://sh.esf.fang.com/housing/__0_0_20000_25000_1_0_0_0/',
        'https://sh.esf.fang.com/housing/__0_0_25000_30000_1_0_0_0/',
        'https://sh.esf.fang.com/housing/__0_0_30000_35000_1_0_0_0/',
        'https://sh.esf.fang.com/housing/__0_0_35000_40000_1_0_0_0/',
        'https://sh.esf.fang.com/housing/__0_0_40000_45000_1_0_0_0/',
        'https://sh.esf.fang.com/housing/__0_0_45000_50000_1_0_0_0/',
        'https://sh.esf.fang.com/housing/__0_0_50000_55000_1_0_0_0/',
        'https://sh.esf.fang.com/housing/__0_0_55000_60000_1_0_0_0/',
        'https://sh.esf.fang.com/housing/__0_0_60000_70000_1_0_0_0/',
        'https://sh.esf.fang.com/housing/__0_0_70000_80000_1_0_0_0/',
        'https://sh.esf.fang.com/housing/__0_0_80000_0_1_0_0_0/'
    ]

    custom_settings = {
        'FEED_EXPORT_FIELDS': ['ID', 'Location', 'Baidu_Coordinates', 'Baidu_Latitude', 'Baidu_Longitude',
                               'WGS_Coordinates', 'WGS_Latitude', 'WGS_Longitude', 'Average_Price_Yuan_Meter',
                               'Average_Price_Yuan_Feet', 'Average_Price_Dollar_Feet', 'Total_Buildings',
                               'Total_Houses', 'Building_Age', 'URL', 'Baidu_Map_Link'],
        'ROBOTSTXT_OBEY': False
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Referer': 'http://search.fang.com/captcha-fa0fc56883/redirect?h={}'
    }
    cookies = {
        'global_cookie': 'airb7gfhk6nsxseligzh4na5l20jza9hupr',
        'g_sourcepage': 'esf_xq%5Elb_pc',
        '__utma': '147393320.206904568.1565727201.1565727201.1565727201.1',
        '__utmc': '147393320',
        '__utmz': '147393320.1565727201.1.1.utmcsr=search.fang.com|utmccn=(referral)|utmcmd=referral|utmcct=/captcha-fa0fc56883/',
        'unique_cookie': 'U_airb7gfhk6nsxseligzh4na5l20jza9hupr*6'
    }

    prod_rank = 0
    location_coordinates = ['']

    def start_requests(self):
        for url in self.start_urls:
            self.headers['Referer'] = self.headers['Referer'].format(url)
            yield scrapy.Request(url=url, headers=self.headers, cookies=self.cookies, callback=self.parse)

    def parse(self, response):
        next_link = response.xpath('//a[@id="PageControl1_hlk_next"]/@href').extract()
        if next_link:
            n_url = response.urljoin(next_link[0])
            yield scrapy.Request(url=n_url, callback=self.parse)

        product_links = response.xpath('//dl[@class="plotListwrap clearfix"]/dt/a/@href').extract()
        for link in product_links:
            url = 'https:{}'.format(link)
            yield scrapy.Request(url=url, callback=self._parse_map_box_url)

    def _parse_map_box_url(self, response):
        item = Fangtem()

        building_info = response.xpath('//div[@class="Rinfolist"]/ul/li//text()').extract()
        total_houses = None
        for label in building_info:
            if '户' in label:
                total_houses = label.replace('户', '')
                break

        map_box_url = response.xpath('//div[@id="map_box"]/iframe/@src').extract()
        map_box_url = 'https:{}'.format(map_box_url[0]) if map_box_url else None
        if map_box_url:
            item['Baidu_Map_Link'] = map_box_url
            item['URL'] = response.url
            item['Total_Houses'] = total_houses

            yield scrapy.Request(
                url=map_box_url,
                callback=self._parse_product,
                meta={
                    'item': item
                }
            )

    def _parse_product(self, response):
        product_json_str = re.search('mainBuilding=(.*?);</script>', str(response.body), re.DOTALL).group(1)
        product_json = json.loads(product_json_str)

        # parse baidu coordinates
        baidu_latitude = product_json.get('baidu_coord_y', None)
        baidu_longitude = product_json.get('baidu_coord_x', None)
        baidu_coordinates = '{lat}, {lot}'.format(lat=baidu_latitude, lot=baidu_longitude)

        # parse price
        average_price_yuan_meter = product_json.get('price_num', None)

        if average_price_yuan_meter:
            item = response.meta.get('item')

            self.prod_rank += 1
            location = self._parse_location_id(
                coord=baidu_coordinates
            )
            wgs_latitude, wgs_longitude = self._parse_wgs_coordinates(
                b_coord_x=baidu_latitude,
                b_coord_y=baidu_longitude
            )
            wgs_coordinates = '{lat}, {lot}'.format(lat=wgs_latitude, lot=wgs_longitude)

            average_price_yuan_feet = float(average_price_yuan_meter) / 10.76
            average_price_dollar_feet = average_price_yuan_feet * 0.15

            total_buildings = product_json.get('buildingtotal', None)

            building_age = product_json.get('finishdate', None)

            item['ID'] = self.prod_rank
            item['Location'] = location
            item['Baidu_Coordinates'] = baidu_coordinates
            item['Baidu_Latitude'] = baidu_latitude
            item['Baidu_Longitude'] = baidu_longitude
            item['WGS_Coordinates'] = wgs_coordinates
            item['WGS_Latitude'] = wgs_latitude
            item['WGS_Longitude'] = wgs_longitude
            item['Average_Price_Yuan_Meter'] = average_price_yuan_meter
            item['Average_Price_Yuan_Feet'] = average_price_yuan_feet
            item['Average_Price_Dollar_Feet'] = average_price_dollar_feet
            item['Total_Buildings'] = total_buildings
            item['Building_Age'] = building_age

            yield item

    def _parse_location_id(self, coord):
        if coord not in self.location_coordinates:
            self.location_coordinates.append(coord)
        return self.location_coordinates.index(coord)

    @staticmethod
    def _parse_wgs_coordinates(b_coord_x, b_coord_y):
        wgs_coord = eviltransform.bd2wgs(
            float(b_coord_x),
            float(b_coord_y)
        )
        return wgs_coord[0], wgs_coord[1]
