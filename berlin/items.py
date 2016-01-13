# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy



class BerlinItem(scrapy.Item):
    headline = scrapy.Field()
    time = scrapy.Field()
    place = scrapy.Field()
    author = scrapy.Field()
    body = scrapy.Field() 
    url = scrapy.Field()
