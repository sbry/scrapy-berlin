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
                            self['time'].strftime('%Y'),
                            '%s-%s.%s'%(self['source_name'], self['source_id'], extension)) 
    pass


def normalize_space(value):
    return value.replace("\n", " ").replace("  ", " ")

def normalize_place(value):
    if not ( value in ['False']
             or value.startswith('Gemeinsam')
             or value.startswith('Tatzeit' ) ):
        yield value.replace(" ", "").replace(',', '/')

class BerlinItemLoader(ItemLoader):
    default_item_class = BerlinItem
    default_output_processor = TakeFirst()
    body_in = MapCompose(normalize_space)
    place_in = MapCompose(normalize_place)
    place_out = Join()

if __name__ == '__main__':
    print BerlinItem.fields
    pass
