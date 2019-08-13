# -*- coding: utf-8 -*-
import scrapy
import re
import json
import eviltransform
import traceback

from real_estate_scraper.items import Fangtem


class FangFSSpider(scrapy.Spider):
    name = 'fang_fs'
    allowed_domains = ['fang.com']
    start_urls = [
        'https://fs.esf.fang.com/housing/__0_0_0_6000_1_0_0_0/',
        'https://fs.esf.fang.com/housing/__0_0_6000_10000_1_0_0_0/',
        'https://fs.esf.fang.com/housing/__0_0_10000_15000_1_0_0_0/',
        'https://fs.esf.fang.com/housing/__0_0_15000_20000_1_0_0_0/',
        'https://fs.esf.fang.com/housing/__0_0_20000_25000_1_0_0_0/',
        'https://fs.esf.fang.com/housing/__0_0_25000_0_1_0_0_0/',
    ]

    custom_settings = {
        'FEED_EXPORT_FIELDS': ['ID', 'Name', 'Type', 'Address', 'Location', 'Baidu_Coordinates', 'Baidu_Latitude',
                               'Baidu_Longitude', 'WGS_Coordinates', 'WGS_Latitude', 'WGS_Longitude',
                               'Average_Price_Yuan_Meter', 'Average_Price_Yuan_Feet', 'Average_Price_Dollar_Feet',
                               'Total_Buildings', 'Total_Houses', 'Building_Age', 'URL', 'Baidu_Map_Link'],
        'ROBOTSTXT_OBEY': False
    }

    prod_rank = 0
    location_coordinates = ['']

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

        b_type = response.xpath('//div[@class="Rinfolist"]/ul/li[b[contains(text(), "建筑类型")]]/text()').extract_first()

        total_houses = response.xpath('//div[@class="Rinfolist"]'
                                      '/ul/li[b[contains(text(), "房屋总数")]]/text()').extract_first()
        total_houses = total_houses.replace('户', '') if total_houses else None

        map_box_url = response.xpath('//div[@id="map_box"]/iframe/@src').extract()
        map_box_url = 'https:{}'.format(map_box_url[0]) if map_box_url else None
        if map_box_url:
            item['Baidu_Map_Link'] = map_box_url
            item['URL'] = response.url
            item['Total_Houses'] = total_houses
            item['Type'] = b_type

            yield scrapy.Request(
                url=map_box_url,
                callback=self._parse_product,
                meta={
                    'item': item
                }
            )

    def _parse_product(self, response):
        product_json_str = re.search('mainBuilding=(.*?);</script>', str(response.body), re.DOTALL).group(1)
        try:
            product_json = json.loads(product_json_str)
        except:
            self.log('Can not load the json data: {}'.format(traceback.format_exc()))
        else:
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

                name = product_json.get('title', None)
                name = name.encode('utf8').decode('unicode_escape') if name else None

                address = product_json.get('address', None)
                address = address.encode('utf8').decode('unicode_escape') if address else None

                item['ID'] = self.prod_rank
                item['Name'] = name
                item['Address'] = address
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
