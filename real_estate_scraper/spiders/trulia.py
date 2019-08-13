# -*- coding: utf-8 -*-
import scrapy
import re
import json

from json.decoder import JSONDecodeError

from real_estate_scraper.items import TruliaItem


class TruliaSpider(scrapy.Spider):
    name = 'trulia'
    allowed_domains = ['www.trulia.com']
    start_urls = [
        'https://www.trulia.com/for_sale/Miami,FL/0-1100000_price/{page_num}_p/',
        'https://www.trulia.com/for_sale/Miami,FL/1100000p_price/{page_num}_p/'
    ]

    headers = {
        'X-Crawlera-Max-Retries': 3,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
        'upgrade-insecure-requests': 1
    }

    custom_settings = {
        'FEED_EXPORT_FIELDS': ['ID', 'Area_Size', 'Bathrooms', 'Bedrooms', 'Coordinates', 'Latitude', 'Longitude',
                               'Region', 'Locality', 'Street_Address', 'ZIP', 'Price', 'URL']
    }

    product_rank = 0

    def start_requests(self):
        self.product_rank = 0
        for url in self.start_urls:
            yield scrapy.Request(
                url=url.format(
                    page_num=1
                ),
                callback=self.parse,
                meta={
                    'page_num': 1,
                    'total_pages': 1
                },
                headers=self.headers
            )

    def parse(self, response):
        page_num = response.meta.get('page_num', 1)
        total_pages = response.meta.get('total_pages', 1)
        if total_pages == 1:
            total_pages = response.xpath('//li[@data-testid="pagination-page-link"]'
                                         '//div/text()').extract()
            total_pages = int(total_pages[-1]) if total_pages else 1

        if total_pages != 1 and page_num < total_pages:
            if page_num == 1:
                url = '{base_url}{page_num}_p/'.format(
                    base_url=response.url,
                    page_num=page_num + 1
                )
            else:
                url = response.url.replace('{}_p'.format(page_num), '{}_p'.format(page_num + 1))

            page_num += 1
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    'page_num': page_num,
                    'total_pages': total_pages
                },
                headers=self.headers
            )

        product_elements = response.xpath('//div[contains(@data-testid, "srp-home-card")]')

        for _product in product_elements:

            product_json_str = _product.xpath('.//script/text()').extract_first()
            product_json = json.loads(product_json_str) if product_json_str else {}

            self.product_rank += 1
            item = TruliaItem()

            # parse price
            price = _product.xpath('.//div[@data-testid="property-price"]/text()').extract_first()

            # parse street address
            street = product_json.get('address', {}).get('streetAddress', None)

            # parse bedrooms and bathrooms
            beds = _product.xpath('.//div[@data-testid="property-beds"]/text()').extract_first()
            beds = beds.replace('bd', '') if beds else None

            baths = _product.xpath('.//div[@data-testid="property-baths"]/text()').extract_first()
            baths = baths.replace('ba', '') if baths else None

            # parse area size in sqr feet
            area_feet = _product.xpath('.//div[@data-testid="property-floorSpace"]/text()').extract_first()
            area_feet = area_feet.replace('sqft', '') if area_feet else None

            # parse region
            region = product_json.get('address', {}).get('addressRegion', 'NY')

            # parse zip code
            zip_code = product_json.get('address', {}).get('postalCode', None)

            # parse coordinates
            coordinates = product_json.get('geo', {})
            lat = coordinates.get('latitude', None)
            long = coordinates.get('longitude', None)

            coordinates = {
                'lat': lat,
                'long': long
            }

            # parse locality
            locality = product_json.get('address', {}).get('addressLocality', None)

            item['ID'] = self.product_rank
            item['Coordinates'] = coordinates
            item['Latitude'] = lat
            item['Longitude'] = long
            item['Street_Address'] = street
            item['Locality'] = locality
            item['Region'] = region
            item['ZIP'] = zip_code
            item['Price'] = price
            item['Area_Size'] = area_feet
            item['Bedrooms'] = beds
            item['Bathrooms'] = baths
            item['URL'] = response.urljoin(
                _product.xpath('.//div[@data-testid="home-card-sale"]/a/@href').extract_first()
            )

            yield item
