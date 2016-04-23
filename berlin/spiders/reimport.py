# -*- coding: utf-8 -*-
import scrapy
from scrapy.cmdline import execute
from berlin.items import BerlinItemLoader
##
# for extracting the id        
import re
from datetime import datetime
import os
import glob
import logging

class ReimportSpider(scrapy.Spider):
    """processing the archive, just wrapping up"""
    name = "reimport"
    ##
    # I learned not to use XML for my own storage but rather native python pickle http://stackoverflow.com/questions/34971287/use-scrapy-to-crawl-local-xml-file-start-url-local-file-address
    def start_requests(self):
        """get requests from the files"""
        for fn in glob.glob(os.getenv('SCRAPY_DATADIR') + '/*/*.xml'):
            yield scrapy.Request('file://%s'%fn, callback=self.parse)
    def parse(self, response):
        parts = {}
        parts['place'] = None
        parts['author'] = 'Polizei Berlin'
        parts['source_name'] = 'polizei'
        parts['source_url'] = dj_au_obj.xpath('field[@name = "source_url"]/text()').extract_first()
        parts['source_id'] = dj_au_obj.xpath('field[@name = "source_url"]/text()').re_first('(\d+)/index\.html')
        parts['place'] = dj_au_obj.xpath('field[@name = "district"]/text()').extract_first()
        parts['time'] = datetime.strptime(pub_date , "%Y-%m-%d %H:%M:%S")

        parts['headline']  = dj_art_obj.xpath('field[@name = "name"]/text()').extract_first()
        parts['body'] = dj_art_obj.xpath('field[@name = "content"]/text()').extract_first()
        item_loader = BerlinItemLoader()
        item_loader.add_value(None, parts)
        yield item_loader.load_item()
    pass

