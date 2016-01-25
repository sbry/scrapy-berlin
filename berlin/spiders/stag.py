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
        for dj_au_obj in response.xpath('/django-objects/object[@model = "stag.augmentedarticlescraperpolizeiberlin"]'):
            logging.log(logging.INFO, "Parsing Polizei-Django-Objects")
            parts = { 'place': 'Berlin',
                      'author': 'Polizei Berlin',
                      'source_name': 'polizei' } 
            ##
            # handle the url 
            full_url = dj_au_obj.xpath('field[@name = "source_url"]/text()').extract()[0]
            logging.log(logging.WARNING, "old URL %s"%full_url)
            match = re.search('(\d+)/index\.html', full_url)
            parts['source_id'] = match.group(1)
            parts['url'] = full_url
            parts['place'] = dj_au_obj.xpath('field[@name = "district"]/text()').extract()[0]
            ##
            # we select the payload-article
            # now we need to resolve the id for more data
            article_id = dj_au_obj.xpath('field[@to = "article.article"]/text()').extract()[0]
            dj_art_obj = response.xpath('/django-objects/object[@pk = "%s"]'%article_id)
            ##
            # send the timestamp in "meta" (recommended procedure)
            pub_date = dj_art_obj.xpath('field[@name = "date_published"]/text()').extract()[0]
            parts['time'] = datetime.strptime(pub_date , "%Y-%m-%d %H:%M:%S")
            ##
            #
            item_loader = BerlinItemLoader(selector = dj_art_obj)
            item_loader.add_xpath('headline', 'field[@name = "name"]/text()')
            item_loader.add_xpath('body', 'field[@name = "content"]/text()')
            ##
            # and add the parts
            item_loader.add_value(None, parts)
            yield item_loader.load_item()
        for dj_au_obj in response.xpath('/django-objects/object[@model = "stag.augmentedarticlescraperbvgaugenblicke"]'):
            logging.log(logging.INFO, "Parsing Bvg-Django-Objects")
            parts = { 'place': 'Berlin',
                      'source_name': 'bvg' } 
            ##
            # handle the url 
            full_url = dj_au_obj.xpath('field[@name = "source_url"]/text()').extract()[0]
            logging.log(logging.WARNING, "old URL %s"%full_url)
            match = re.search('(\d+)\.html', full_url)
            parts['source_id'] = match.group(1)
            parts['url'] = full_url
            parts['place'] = dj_au_obj.xpath('field[@name = "place"]/text()').extract()[0]
            parts['author'] = dj_au_obj.xpath('field[@name = "username"]/text()').extract()[0]
            ##
            # send the timestamp in "meta" (recommended procedure)
            pub_date = dj_au_obj.xpath('field[@name = "time"]/text()').extract()[0]
            parts['time'] = datetime.strptime(pub_date , "%Y-%m-%d %H:%M:%S")
            ##
            # we select the payload-article
            # now we need to resolve the id for more data
            article_id = dj_au_obj.xpath('field[@to = "article.article"]/text()').extract()[0]
            dj_art_obj = response.xpath('/django-objects/object[@pk = "%s"]'%article_id)
            ##
            #
            item_loader = BerlinItemLoader(selector = dj_art_obj)
            item_loader.add_xpath('headline', 'field[@name = "name"]/text()')
            item_loader.add_xpath('body', 'field[@name = "content"]/text()')
            ##
            # and add the parts
            item_loader.add_value(None, parts)
            yield item_loader.load_item()
        pass
    pass

