# -*- coding: utf-8 -*-
import scrapy
import re
import json
from real_estate_scraper.items import PropertyFinderItem


class PropertyFinderSpider(scrapy.Spider):
    name = 'property_finder'
    allowed_domains = ['propertyfinder.ae']
    start_urls = [
        'https://www.propertyfinder.ae/en/search?c=1&l=4-1&ob=mr&page=1',
    ]
    product_rank = 0

    custom_settings = {
        'FEED_EXPORT_FIELDS': ['ID', 'Title', 'Title_2', 'Reference', 'Company', 'ORN', 'BRN',
                               'Price', 'Type', 'Trakheesi_Permit', 'Completion_Status', 'Bedrooms', 'Bathrooms',
                               'Area_Sqft', 'Coordinate_X', 'Coordinate_Y']
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        next_page_link = response.xpath('//a[@class="pagination__link pagination__link--next"]/@href').extract()
        next_page_link = response.urljoin(next_page_link[0]) if next_page_link else None

        if next_page_link:
            yield scrapy.Request(url=next_page_link, callback=self.parse)

        products = response.xpath('//a[@class="card card-clickable"]/@href').extract()
        for product in products:
            product_link = response.urljoin(product)
            yield scrapy.Request(url=product_link, callback=self._parse_product)

    def _parse_product(self, response):
        item = PropertyFinderItem()
        self.product_rank += 1

        title = response.xpath('//h1[@class="property-header__title--detail"]/text()').extract_first()

        title_2 = response.xpath('//h2[@class="property-header__sub-title"]/text()').extract_first()

        reference = response.xpath('//div[@class="property-header__reference"]//strong/text()').extract_first()

        company = response.xpath(
            '//div[@class="agent-info__detail-content agent-info__detail-content--bold"]/text()'
        ).extract_first()

        orn = response.xpath('//div[@class="column--secondary"]'
                             '/div[@class="agent-info-contact"]'
                             '//div[@class="agent-info__detail-item" and span[contains(text(), "ORN")]]'
                             '/div[@class="agent-info__detail-content"]/text()').extract_first()

        brn = response.xpath('//div[@class="column--secondary"]'
                             '/div[@class="agent-info-contact"]'
                             '//div[@class="agent-info__detail-item" and span[contains(text(), "BRN")]]'
                             '/div[@class="agent-info__detail-content"]/text()').extract_first()

        price = response.xpath('//span[@class="facts__content--price-value"]/text()').re_first('[\d,]+')

        type = response.xpath('//div[@class="facts__list-item" '
                              'and div[@class="facts__label" and contains(text(), "Type")]]'
                              '/div[@class="facts__content"]/text()').extract_first()

        trakheesi_permit = response.xpath('//div[@class="facts__list-item" '
                                          'and div[@class="facts__label facts__label-info-area" '
                                          'and contains(text(), "Trakheesi Permit")]]'
                                          '/div[@class="facts__content"]/text()').extract_first()

        completion_status = response.xpath('//div[@class="facts__list-item" '
                                           'and div[@class="facts__label" and contains(text(), "Completion status")]]'
                                           '/div[@class="facts__content"]/text()').extract_first()

        bedrooms = response.xpath('//div[@class="facts__list-item" '
                                  'and div[@class="facts__label" and contains(text(), "Bedrooms")]]'
                                  '/div[@class="facts__content"]/text()').extract_first()

        bathrooms = response.xpath('//div[@class="facts__list-item" '
                                   'and div[@class="facts__label" and contains(text(), "Bathrooms")]]'
                                   '/div[@class="facts__content"]/text()').extract_first()

        area_size = response.xpath('//div[@class="facts__list-item" '
                                   'and div[@class="facts__label" and contains(text(), "Area")]]'
                                   '/div[@class="facts__content"]/text()').extract_first()
        area_size = area_size.split('/')[0].strip() if area_size else None

        coord_json_str = re.search('(\[{"@context.*?)</script>', response.body_as_unicode(), re.DOTALL).group(1)
        if coord_json_str:
            coord_json = json.loads(coord_json_str)
            coord_x = coord_json[1].get('geo', {}).get('latitude') if coord_json else None
            coord_y = coord_json[1].get('geo', {}).get('longitude') if coord_json else None
        else:
            coord_x = None
            coord_y = None

        item['ID'] = self.product_rank
        item['Title'] = title
        item['Title_2'] = title_2
        item['Reference'] = reference
        item['Company'] = company
        item['ORN'] = orn
        item['BRN'] = brn
        item['Price'] = price
        item['Type'] = type
        item['Trakheesi_Permit'] = trakheesi_permit
        item['Completion_Status'] = completion_status
        item['Bedrooms'] = bedrooms
        item['Bathrooms'] = bathrooms
        item['Area_Sqft'] = area_size
        item['Coordinate_X'] = coord_x
        item['Coordinate_Y'] = coord_y

        yield item
