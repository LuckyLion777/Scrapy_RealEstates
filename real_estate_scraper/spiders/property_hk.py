# -*- coding: utf-8 -*-
import scrapy
import re
import json
from real_estate_scraper.items import PropertyHKItem


class PropertyFinderSpider(scrapy.Spider):
    name = 'property_hk'
    allowed_domains = ['property.hk']
    start_urls = [
        'http://w22.property.hk/eng/property_search.php?p={page_num}',
    ]
    product_rank = 0

    custom_settings = {
        'FEED_EXPORT_FIELDS': ['ID', 'Input_Date', 'Usage', 'District', 'Street_ENG', 'Street_CHI', 'Building_ENG',
                               'Building_CHI', 'Floor', 'input_date', 'Gross_Area', 'Salable_Area', 'Price_HKD',
                               'Price_USD', 'Price_SQFT', 'OP_Date', 'Exp_Year', 'Facing', 'Layout', 'Decoration',
                               'Remarks', 'Geo_X', 'Geo_Y', 'URL']
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url, callback=self.parse, meta={
                    'page_num': 1
                }
            )

    def parse(self, response):
        current_page = response.meta.get('page_num', 1)
        if current_page < 1210:
            next_page_link = self.start_urls[0].format(page_num=int(current_page) + 1)
            yield scrapy.Request(
                url=next_page_link, callback=self.parse, meta={
                    'page_num': int(current_page) + 1
                }
            )

        products = response.xpath('//form[@name="printForm"]//table//img/parent::a/@href').extract()
        for product in products:
            product_link = response.urljoin(product)
            yield scrapy.Request(url=product_link, callback=self._parse_product)

    def _parse_product(self, response):
        item = PropertyHKItem()
        self.product_rank += 1

        property_info = response.xpath('//div[@id="property-info"]')

        input_date = property_info.xpath('.//table//tr[1]//td[@class="val"]/text()').extract_first()

        usage = property_info.xpath('.//table//tr[2]//td[@class="val"]/text()').extract_first()

        district = property_info.xpath('.//table//tr[3]//td[@class="val"]/text()').extract_first()

        street_eng = property_info.xpath('.//table//tr[4]//td[@class="val"]/text()').extract_first()

        street_chi = property_info.xpath('.//table//tr[5]//td[@class="val"]/text()').extract_first()

        building_eng = property_info.xpath('.//table//tr[6]//td[@class="val"]/text()').extract_first()

        building_chi = property_info.xpath('.//table//tr[7]//td[@class="val"]/text()').extract_first()

        floor = property_info.xpath('.//table//tr[8]//td[@class="val"]/text()').extract_first()

        block_number = property_info.xpath('.//table//tr[9]//td[@class="val"]/text()').extract_first()

        gross_area = property_info.xpath('.//table//tr[10]//td[@class="val"]/text()').extract_first()

        saleable_area = property_info.xpath('.//table//tr[11]//td[@class="val"]/text()').extract_first()

        price_HKD = property_info.xpath('.//table//tr[12]//td[@class="val"]/text()').extract_first()

        if price_HKD and '--' not in price_HKD:
            if 'Million' in price_HKD:
                price_usd = price_HKD.replace('$', '').replace('Million', '').replace(',', '')
                price_usd = float(price_usd) * 1000000 / 7.84
            else:
                price_usd = price_HKD.replace('$', '').replace(',', '')
                price_usd = float(price_usd) * 1000000 / 7.84
        else:
            price_usd = None
            price_HKD = None

        price_sqft = property_info.xpath('.//table//tr[14]//td[@class="val"]/text()').extract_first()

        op_date = property_info.xpath('.//table//tr[16]//td[@class="val"]/text()').extract_first()

        exp_year = property_info.xpath('.//table//tr[17]//td[@class="val"]/text()').extract_first()

        facing = property_info.xpath('.//table//tr[18]//td[@class="val"]/text()').extract_first()

        layout = property_info.xpath('.//table//tr[19]//td[@class="val"]/text()').extract_first()

        decoration = property_info.xpath('.//table//tr[20]//td[@class="val"]/text()').extract_first()

        remarks = property_info.xpath('.//table//tr[21]//td[@class="val"]/text()').extract_first()

        map = response.xpath('//iframe[@id="map"]/@src').extract_first()
        if map:
            map = re.search('q=(.*?)&zoom', map, re.DOTALL).group(1)
            coord_x = map.split(',')[0]
            coord_y = map.split(',')[1]
        else:
            coord_x = None
            coord_y = None

        item['ID'] = self.product_rank
        item['Input_Date'] = input_date
        item['Usage'] = usage
        item['District'] = district
        item['Street_ENG'] = street_eng
        item['Street_CHI'] = street_chi
        item['Building_ENG'] = building_eng
        item['Building_CHI'] = building_chi
        item['Floor'] = floor
        item['Block_Number'] = block_number
        item['Gross_Area'] = gross_area
        item['Salable_Area'] = saleable_area
        item['Price_HKD'] = price_HKD
        item['Price_USD'] = price_usd
        item['Price_SQFT'] = price_sqft
        item['OP_Date'] = op_date
        item['Exp_Year'] = exp_year
        item['Facing'] = facing
        item['Layout'] = layout
        item['Decoration'] = decoration
        item['Remarks'] = remarks
        item['Geo_X'] = coord_x
        item['Geo_Y'] = coord_y
        item['URL'] = response.url

        yield item
