# -*- coding: utf-8 -*-
import scrapy
from scrapy.cmdline import execute
from berlin.items import BerlinItemLoader
##
# for extracting the id        
import re
from datetime import datetime

class PolizeiSpider(scrapy.Spider):
    name = "polizei"
    allowed_domains = ["www.berlin.de"]
    start_urls = (
        'https://www.berlin.de/polizei/polizeimeldungen/',
    )
    def parse(self, content):
        for href in content.css('li.row-fluid > div:nth-child(2) > a:nth-child(1)::attr("href")'):
            full_url = content.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_item_page)
        pass
    def parse_item_page(self, response):
        selector = response.css('div.article')
        item_loader = BerlinItemLoader(selector = selector)
        ##
        #
        item_loader.add_css('headline', 'h1.title::text')
        item_loader.add_css('place', 'div.polizeimeldung:nth-child(2)::text')
        item_loader.add_css('body', 'div.textile')
        ##
        # the simple parts
        parts = { 'place': 'Berlin', 'author': 'Polizei Berlin', 'url': response.url, 'source_name': self.name}
        ##
        # extract the id from the url
        # http://www.berlin.de/polizei/polizeimeldungen/pressemitteilung.434878.php
        match = re.search('(\d+)\.php$', response.url)
        parts['source_id'] = match.group(1)
        ##
        # parse time time
        raw_time = selector.css('div.polizeimeldung:nth-child(1)::text')
        parts['time'] = datetime.strptime(raw_time.extract()[0], 'Polizeimeldung vom %d.%m.%Y')
        ##
        # and add the parts
        item_loader.add_value(None, parts)
        return item_loader.load_item()
    pass
    

