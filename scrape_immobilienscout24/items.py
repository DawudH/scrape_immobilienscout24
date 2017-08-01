# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ImmobilienscoutItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    bare_price = scrapy.Field()
    additional_costs = scrapy.Field()
    total_price = scrapy.Field()
    build_year = scrapy.Field()
    zipcode = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    neighborhood = scrapy.Field()
    building_type = scrapy.Field()
    property_id = scrapy.Field()
    living_area = scrapy.Field()
    lot_size = scrapy.Field()
    rooms = scrapy.Field()
    pets = scrapy.Field()
    url = scrapy.Field()
    img_url = scrapy.Field()
    title = scrapy.Field()
