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
    source_url = scrapy.Field()
    headline = scrapy.Field()
    time = scrapy.Field()
    place = scrapy.Field()
    author = scrapy.Field()
    body = scrapy.Field()
    # #
    # why not make items nice by default?
    def __getitem__(self, key):
        try:
            return self._values[key]
        except KeyError:
            return ''
    def filename(self, extension='p'):
        """The item's filename is used for serializing"""
        return os.path.join(os.getenv('SCRAPY_DATADIR', '../scrapy-items'),
                            extension, '%s-%s.%s' % (self['source_name'], self['source_id'], extension)) 
    @classmethod
    def analyse_filename(cls, filename):
        (source_name, source_id) = os.path.splitext(os.path.basename(filename))[0].split('-')
        return {
                source_name: source_name,
                source_id: source_id
                }
    pass

class BerlinItemLoader(ItemLoader):
    default_item_class = BerlinItem
    default_output_processor = TakeFirst()
    body_in = MapCompose(lambda v: v.replace("\n", " ").replace("  ", " "))
    place_in = MapCompose(lambda v: v.strip().replace(" - ", "-").replace(',', '/'))
    place_out = Join(separator='/')

if __name__ == '__main__':
    print BerlinItem.fields
    pass
