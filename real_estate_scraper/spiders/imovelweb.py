# -*- coding: utf-8 -*-
import scrapy
from real_estate_scraper.items import ImovelwebItem


class ImovelwebSpider(scrapy.Spider):
    name = 'imovelweb'
    allowed_domains = ['imovelweb.com.br']
    start_urls = [
        'http://www.imovelweb.com.br/apartamentos-venda-sao-paulo-sp-425000-449999-reales.html',
        # 'https://www.imovelweb.com.br/apartamentos-venda-sao-paulo-sp-450000-475000-reales.html',
    ]
    product_rank = 0

    custom_settings = {
        'FEED_EXPORT_FIELDS': ['ID', 'Price_BRA', 'Price_USD', 'Condomin', 'IPTU', 'Type', 'Size',
                               'Quarto', 'Vaga', 'Address', 'Area_Total', 'Banheiro', 'Suite', 'Property', 'Advertiser',
                               'Advertiser_2', 'Cod_Imovel', 'Creci', 'URL']
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)
            # yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        product_urls = response.xpath('//ul[@id="avisos-content"]/li/@data-href').extract()

        current_page = response.xpath('//div[@class="pagination pagination-centered"]'
                                      '//li[@class="active"]/a/text()').extract()
        current_page = current_page[0] if current_page else None

        if current_page and int(current_page) < 1000:
            next_page_link = response.xpath('//li[contains(@class, "pagination-action-next")]/a/@href').extract()
            if next_page_link:
                next_url = response.urljoin(next_page_link[0])
                yield scrapy.Request(url=next_url, callback=self.parse)

        for product_url in product_urls:
            url = response.urljoin(product_url)
            yield scrapy.Request(url=url, callback=self._parse_product)

    def _parse_product(self, response):
        item = ImovelwebItem()
        self.product_rank += 1

        is_development = response.xpath('//div[@class="status-development card-container"]').extract()
        if is_development:
            price_bra = response.xpath('//div[@class="status-development card-container"]'
                                       '//span[@class="data-price"]/b/text()').extract()
            price_bra = price_bra[0].replace('R$ ', '').replace('.', '') if price_bra else None

            price_usd = float(price_bra) / 3.8 if price_bra else None

            condomin = None
            iptu = None
            property_type = 'Property'

            address = response.xpath('//h2[@class="info-location"]//text()').extract()
            address = address[0] if address else None

            area_total = response.xpath('//div[@class="status-development card-container"]'
                                        '//div[@class="status-columns"]'
                                        '/div[@class="column"][2]'
                                        '/div[@class="row"][2]//b/text()').extract()
            area_total = area_total[0].replace('m2', '') if area_total else None

            area_size = response.xpath('//div[@class="status-development card-container"]'
                                       '//div[@class="status-columns"]'
                                       '/div[@class="column"][1]'
                                       '/div[@class="row"][2]//b/text()').extract()
            area_size = area_size[0].replace('m2', '') if area_size else None

            banheiro = None

            vaga = response.xpath('//div[@class="status-development card-container"]'
                                  '//div[@class="status-columns"]'
                                  '/div[@class="column"][2]'
                                  '/div[@class="row"][3]//b/text()').extract()
            vaga = vaga[0] if vaga else None

            quarto = response.xpath('//div[@class="status-development card-container"]'
                                    '//div[@class="status-columns"]'
                                    '/div[@class="column"][2]'
                                    '/div[@class="row"][1]//b/text()').extract()
            quarto = quarto[0] if quarto else None

            suite = None

            advertiser = response.xpath('//section[contains(@class, "publisher-section")]'
                                        '//h3[@class="publisher-subtitle"]/b/text()').extract()
            advertiser = advertiser[0] if advertiser else None

            advertiser_id = response.xpath('//section[contains(@class, "publisher-section")]'
                                           '//span[@class="publisher-code"][1]/text()').extract()
            advertiser_id = advertiser_id[0] if advertiser_id else None

            cod_imovel = response.xpath('//section[contains(@class, "publisher-section")]'
                                        '//span[@class="publisher-code"][2]/text()').extract()
            cod_imovel = cod_imovel[0] if cod_imovel else None

            creci = response.xpath('//section[contains(@class, "publisher-section")]'
                                   '//span[@class="publisher-code"][3]/text()').extract()
            creci = creci[0] if creci else None

            item['ID'] = self.product_rank
            item['Price_BRA'] = price_bra
            item['Price_USD'] = price_usd
            item['Condomin'] = condomin
            item['IPTU'] = iptu
            item['Type'] = property_type
            item['Size'] = area_size
            item['Quarto'] = quarto
            item['Vaga'] = vaga
            item['Address'] = address
            item['Area_Total'] = area_total
            item['Banheiro'] = banheiro
            item['Suite'] = suite
            item['Property'] = 1
            item['Advertiser'] = advertiser
            item['Advertiser_2'] = advertiser_id
            item['Cod_Imovel'] = cod_imovel
            item['Creci'] = creci
            item['URL'] = response.url

            yield item
        else:
            price_bra = response.xpath('//div[@class="block-price-container"]'
                                       '//div[@class="block-price block-row"][1]'
                                       '//span/text()').extract()
            price_bra = price_bra[0].replace('R$ ', '').replace('.', '') if price_bra else None

            price_usd = float(price_bra) / 3.8 if price_bra else None

            condomin = response.xpath('//div[@class="block-price-container"]'
                                      '//div[@class="block-expensas block-row"][1]'
                                      '//span/text()').extract()
            condomin = condomin[0].replace('R$ ', '').replace('.', '') if condomin else None

            iptu = response.xpath('//div[@class="block-price-container"]'
                                  '//div[@class="block-expensas block-row"][2]'
                                  '//span/text()').extract()
            iptu = iptu[0].replace('R$ ', '').replace('.', '') if iptu else None

            property_info = response.xpath('//h2[@class="title-type-sup"]/b/text()').extract()
            property_info = property_info[0].split('·') if property_info else None

            property_type = property_info[0] if property_info else None

            addresses = response.xpath('//h2[@class="title-location"]//text()').extract()
            address = ''
            for _address in addresses:
                address += _address

            area_total = response.xpath('//i[@class="icon-f icon-f-stotal"]/../b/text()').extract()
            area_total = area_total[0].replace('m2', '') if area_total else None

            area_size = response.xpath('//i[@class="icon-f icon-f-scubierta"]/../b/text()').extract()
            area_size = area_size[0].replace('m2', '') if area_size else None

            banheiro = response.xpath('//i[@class="icon-f icon-f-bano"]/../b/text()').extract()
            banheiro = banheiro[0] if banheiro else None

            vaga = response.xpath('//i[@class="icon-f icon-f-cochera"]/../b/text()').extract()
            vaga = vaga[0] if vaga else None

            quarto = response.xpath('//i[@class="icon-f icon-f-dormitorio"]/../b/text()').extract()
            quarto = quarto[0] if quarto else None

            suite = response.xpath('//i[@class="icon-f icon-f-toilete"]/../b/text()').extract()
            suite = suite[0] if suite else None

            advertiser = response.xpath('//section[contains(@class, "publisher-section")]'
                                        '//h3[@class="publisher-subtitle"]/b/text()').extract()
            advertiser = advertiser[0] if advertiser else None

            advertiser_id = response.xpath('//section[contains(@class, "publisher-section")]'
                                           '//span[@class="publisher-code"][1]/text()').extract()
            advertiser_id = advertiser_id[0] if advertiser_id else None

            cod_imovel = response.xpath('//section[contains(@class, "publisher-section")]'
                                        '//span[@class="publisher-code"][2]/text()').extract()
            cod_imovel = cod_imovel[0] if cod_imovel else None

            creci = response.xpath('//section[contains(@class, "publisher-section")]'
                                   '//span[@class="publisher-code"][3]/text()').extract()
            creci = creci[0] if creci else None

            item['ID'] = self.product_rank
            item['Price_BRA'] = price_bra
            item['Price_USD'] = price_usd
            item['Condomin'] = condomin
            item['IPTU'] = iptu
            item['Type'] = property_type
            item['Size'] = area_size
            item['Quarto'] = quarto
            item['Vaga'] = vaga
            item['Address'] = address
            item['Area_Total'] = area_total
            item['Banheiro'] = banheiro
            item['Suite'] = suite
            item['Property'] = -1
            item['Advertiser'] = advertiser
            item['Advertiser_2'] = advertiser_id
            item['Cod_Imovel'] = cod_imovel
            item['Creci'] = creci
            item['URL'] = response.url

            yield item
