# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TruliaItem(scrapy.Item):
    ID = scrapy.Field()
    Coordinates = scrapy.Field()
    Latitude = scrapy.Field()
    Longitude = scrapy.Field()
    Street_Address = scrapy.Field()
    Locality = scrapy.Field()
    Region = scrapy.Field()
    ZIP = scrapy.Field()
    Price = scrapy.Field()
    Area_Size = scrapy.Field()
    Bedrooms = scrapy.Field()
    Bathrooms = scrapy.Field()
    URL = scrapy.Field()


class Fangtem(scrapy.Item):
    ID = scrapy.Field()
    Name = scrapy.Field()
    Type = scrapy.Field()
    Address = scrapy.Field()
    Location = scrapy.Field()
    Baidu_Coordinates = scrapy.Field()
    WGS_Coordinates = scrapy.Field()
    Baidu_Latitude = scrapy.Field()
    Baidu_Longitude = scrapy.Field()
    WGS_Latitude = scrapy.Field()
    WGS_Longitude = scrapy.Field()
    Average_Price_Yuan_Meter = scrapy.Field()
    Average_Price_Yuan_Feet = scrapy.Field()
    Average_Price_Dollar_Feet = scrapy.Field()
    Total_Buildings = scrapy.Field()
    Total_Houses = scrapy.Field()
    Building_Age = scrapy.Field()
    URL = scrapy.Field()
    Baidu_Map_Link = scrapy.Field()
    Property_Company = scrapy.Field()
    Developer = scrapy.Field()



class ImovelwebItem(scrapy.Item):
    ID = scrapy.Field()
    Price_BRA = scrapy.Field()
    Price_USD = scrapy.Field()
    Condomin = scrapy.Field()
    IPTU = scrapy.Field()
    Type = scrapy.Field()
    Size = scrapy.Field()
    Quarto = scrapy.Field()
    Vaga = scrapy.Field()
    Address = scrapy.Field()
    Area_Total = scrapy.Field()
    Banheiro = scrapy.Field()
    Suite = scrapy.Field()
    Property = scrapy.Field()
    Advertiser = scrapy.Field()
    Advertiser_2 = scrapy.Field()
    Cod_Imovel = scrapy.Field()
    Creci = scrapy.Field()
    URL = scrapy.Field()


class PropertyFinderItem(scrapy.Item):
    ID = scrapy.Field()
    Title = scrapy.Field()
    Title_2 = scrapy.Field()
    Reference = scrapy.Field()
    Company = scrapy.Field()
    ORN = scrapy.Field()
    BRN = scrapy.Field()
    Price = scrapy.Field()
    Type = scrapy.Field()
    Trakheesi_Permit = scrapy.Field()
    Completion_Status = scrapy.Field()
    Bedrooms = scrapy.Field()
    Bathrooms = scrapy.Field()
    Area_Sqft = scrapy.Field()
    Coordinate_X = scrapy.Field()
    Coordinate_Y = scrapy.Field()


class PropertyHKItem(scrapy.Item):
    ID = scrapy.Field()
    Input_Date = scrapy.Field()
    Usage = scrapy.Field()
    District = scrapy.Field()
    Street_ENG = scrapy.Field()
    Street_CHI = scrapy.Field()
    Building_ENG = scrapy.Field()
    Building_CHI = scrapy.Field()
    Floor = scrapy.Field()
    Block_Number = scrapy.Field()
    Gross_Area = scrapy.Field()
    Salable_Area = scrapy.Field()
    Price_HKD = scrapy.Field()
    Price_USD = scrapy.Field()
    Price_SQFT = scrapy.Field()
    OP_Date = scrapy.Field()
    Exp_Year = scrapy.Field()
    Facing = scrapy.Field()
    Layout = scrapy.Field()
    Decoration = scrapy.Field()
    Remarks = scrapy.Field()
    Geo_X = scrapy.Field()
    Geo_Y = scrapy.Field()
    URL = scrapy.Field()
