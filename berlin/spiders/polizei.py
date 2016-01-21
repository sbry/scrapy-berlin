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
    ##
    # we parse the rss-feed for the date-created timestamp
    start_urls = (
        'https://www.berlin.de/polizei/polizeimeldungen/index.php/rss',
    )       
    def parse(self, response):
        for rss_item in response.xpath('//item'):
            full_url = rss_item.xpath('link/text()').extract()[0]
            request = scrapy.Request(full_url, callback=self.parse_item_page)
            ##
            # send the timestamp in "meta" (recommended procedure)
            pub_date = rss_item.xpath('pubDate/text()').extract()[0]
            pub_date = "-".join(pub_date.split()[1:5])
            request.meta['time'] = datetime.strptime(pub_date , "%d-%b-%Y-%H:%M:%S")
            ##
            # does not work (ValueError: 'z' is a bad directive in format '%a, %d %b %Y %H:%M:%S %z')
            # request.meta['time'] = datetime.strptime(pub_date , "%a, %d %b %Y %H:%M:%S %z")
            yield request
        pass
    def parse_item_page(self, response):
        ##
        # retrieve what we sent
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
        if response.meta['time']:
            parts['time'] = response.meta['time']
        else:
            raw_time = selector.css('div.polizeimeldung:nth-child(1)::text')
            parts['time'] = datetime.strptime(raw_time.extract()[0], 'Polizeimeldung vom %d.%m.%Y')
        ##
        # and add the parts
        item_loader.add_value(None, parts)
        return item_loader.load_item()
    pass

