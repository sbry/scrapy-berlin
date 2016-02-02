# -*- coding: utf-8 -*-
import scrapy
from scrapy.cmdline import execute
from berlin.items import BerlinItemLoader, BerlinItem
##
# for extracting the id        
import re
from datetime import datetime

class PolizeiSpider(scrapy.Spider):
    name = "polizei"
    allowed_domains = ["www.berlin.de"]
    ##
    # we parse the rss-feed for the date-created timestamp
    start_urls = (
        'https://www.berlin.de/polizei/polizeimeldungen/index.php/rss',
    )       
    def parse(self, response):
        for rss_item in response.xpath('//item'):
            parts = {}
            source_url = rss_item.xpath('link/text()').extract_first()
            parts['source_url'] = source_url

            ##
            # extract the id from the url
            # http://www.berlin.de/polizei/polizeimeldungen/pressemitteilung.434878.php
            match = re.search('(\d+)\.php$', source_url)
            parts['source_id'] = match.group(1)
            parts['source_name'] = self.name
            ##
            # send the timestamp in "meta" (recommended procedure)            
            pub_date = rss_item.xpath('pubDate/text()').extract_first()
            ##
            # From: http://stackoverflow.com/questions/31005207/transform-pubdate-to-string-in-python
            pub_date = "-".join(pub_date.split()[1:5])
            parts['time'] = datetime.strptime(pub_date , "%d-%b-%Y-%H:%M:%S")
            #
            # direct matching does not work even though it should imo
            # request.meta['time'] = datetime.strptime(pub_date , "%a, %d %b %Y %H:%M:%S %z")
            # -> ValueError: 'z' is a bad directive in format '%a, %d %b %Y %H:%M:%S %z'
            request = scrapy.Request(source_url, callback=self.parse_item_page)
            request.meta['parts'] = parts
            yield request
        pass
    def parse_item_page(self, response):
        ##
        # retrieve what we sent
        selector = response.css('div.article')
        item_loader = BerlinItemLoader(selector = selector)
        ##
        # the simple parts
        parts = response.meta['parts']
        parts['place'] = self.parse_item_page_place(response)
        parts['author'] = 'Polizei Berlin'
        item_loader.add_value(None, parts)
        ##
        #
        item_loader.add_css('headline', 'h1.title::text')
        item_loader.add_css('body', 'div.textile')
        return item_loader.load_item()
    def parse_item_page_place(self, response):
        """we know nothing so we do default and fallback and might add here when stuff goes wrong"""
        place = response.css('div.polizeimeldung:nth-child(2)::text').extract_first()
        if not place:
            place = response.css('.textile>p>strong::text').extract_first()        
        return place.strip(' ()')
    pass

