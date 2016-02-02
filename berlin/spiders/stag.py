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

class StagSpider(scrapy.Spider):
    """processing the archive, just wrapping up"""
    name = "stag"
    ##
    # http://stackoverflow.com/questions/34971287/use-scrapy-to-crawl-local-xml-file-start-url-local-file-address
    def start_requests(self):
        """get requests from the files"""
        for fn in glob.glob(os.getenv('STAGGER_DIR', '../sams-tagger') + '/*.xml'):
            yield scrapy.Request('file://%s'%fn, callback=self.parse)
    def parse(self, response):
        """this is the dump of a cms running on django nonrel and google appengine I  wrote in 2010 or s/t. Appengine got too expensive for me."""
        logging.log(logging.INFO, "Parsed XML-Input-File %s"%response.url)
        ##
        # bvg is still online, we get e/t from there by recrawling recursively 
        for dj_au_obj in response.xpath('/django-objects/object[@model = "stag.augmentedarticlescraperpolizeiberlin"]'):
            parts = {}
            parts['place'] = None
            parts['author'] = 'Polizei Berlin'
            parts['source_name'] = 'polizei'
            parts['source_url'] = dj_au_obj.xpath('field[@name = "source_url"]/text()').extract_first()
            parts['source_id'] = dj_au_obj.xpath('field[@name = "source_url"]/text()').re_first('(\d+)/index\.html')
            parts['place'] = dj_au_obj.xpath('field[@name = "district"]/text()').extract_first()
            if parts['place'] == 'False':
                parts['place'] = None
            ##
            # select the payload-article
            # now we need to resolve the id for more data
            article_id = dj_au_obj.xpath('field[@to = "article.article"]/text()').extract_first()
            dj_art_obj = response.xpath('/django-objects/object[@pk = "%s"]'%article_id)
            pub_date = dj_art_obj.xpath('field[@name = "date_published"]/text()').extract_first()
            parts['time'] = datetime.strptime(pub_date , "%Y-%m-%d %H:%M:%S")
            parts['headline']  = dj_art_obj.xpath('field[@name = "name"]/text()').extract_first()
            parts['body'] = dj_art_obj.xpath('field[@name = "content"]/text()').extract_first()
            item_loader = BerlinItemLoader()
            item_loader.add_value(None, parts)
            yield item_loader.load_item()


