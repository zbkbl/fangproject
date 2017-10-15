# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FangprojectItem(scrapy.Item):
    name = scrapy.Field()
    location = scrapy.Field()
    totalBuildings = scrapy.Field()
    buildTime = scrapy.Field()
    totalUsers = scrapy.Field()
    propertyType = scrapy.Field()
    accumulationRate = scrapy.Field()
    greenRate = scrapy.Field()
    propertyFee = scrapy.Field()
    developers = scrapy.Field()
    propertyCompany = scrapy.Field()
    adress = scrapy.Field()
    averagePrice = scrapy.Field()
    ave_time = scrapy.Field()
    market = scrapy.Field()
    hospital = scrapy.Field()
    subway = scrapy.Field()
    bus = scrapy.Field()
    parking_space = scrapy.Field()
    url = scrapy.Field()
    school = scrapy.Field()
    city_id = scrapy.Field()
    district = scrapy.Field()
    community = scrapy.Field()
    crawl_time = scrapy.Field()
    school_district = scrapy.Field()

