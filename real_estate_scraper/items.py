# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


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
