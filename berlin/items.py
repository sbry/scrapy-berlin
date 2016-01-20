# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import os, scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, MapCompose, TakeFirst, Identity


class BerlinItem(scrapy.Item):
    source_id = scrapy.Field()
    source_name = scrapy.Field()
    headline = scrapy.Field()
    time = scrapy.Field()
    place = scrapy.Field()
    author = scrapy.Field()
    body = scrapy.Field()
    url = scrapy.Field()
    def filename(self, extension = 'xml'):
        """The item's filename is used for keeping state"""
        return os.path.join(os.getenv('SCRAPY_DATADIR', '../scrapy-items'),
                            self['time'].strftime('%Y/%m/%d'),
                            '%s-%s.%s'%(self['source_name'], self['source_id'], extension)) 
    pass
 

class BerlinItemLoader(ItemLoader):
    default_item_class = BerlinItem
    default_output_processor = TakeFirst()
    
