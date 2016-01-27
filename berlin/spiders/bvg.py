# -*- coding: utf-8 -*-
import scrapy
from scrapy.cmdline import execute
from berlin.items import BerlinItemLoader, BerlinItem
##
# parse the time
from datetime import datetime
##
# for extracting the id from http://blog.scrapinghub.com/2016/01/19/scrapy-tips-from-the-pros-part-1/      
from w3lib.url import url_query_parameter
##
#
import os

import logging

class BvgSpider(scrapy.Spider):
    name = "bvg"
    allowed_domains = ["www.bvg.de"]
    start_urls = (
            'https://www.bvg.de/de/Meine-BVG/Meine-Augenblicke/Alle-Augenblicke',
    )
    def parse(self, content):
        for href in content.css('.moment-table__more > a:nth-child(1)::attr("href")'):
            full_url = content.urljoin(href.extract())
            request = scrapy.Request(full_url, callback=self.parse_item_page)
            ##
            # we save as much as we can in parts which goes into meta
            parts = {}
            parts['source_id'] = url_query_parameter(full_url, 'id')
            parts['source_name'] = self.name
            # <div class="">24.01.2016 um 17:00 Uhr • Peterpower</div>
            pub_date = content.css('.moment-table__datetime::text').extract()[0].partition(' Uhr')[0]
            parts['time'] = datetime.strptime(pub_date , "%d.%m.%Y um %H:%M")
            # here
            request.meta['parts'] = parts
            yield request
        pass
    def parse_item_page(self, response):
        selector = response.css('div.article__body')
        item_loader = BerlinItemLoader(selector = selector)
        ##
        # the simple parts
        parts = response.meta['parts']
        parts['url'] = response.url
        parts['place'],raw_time,unwanted,parts['author'],parts['headline'] \
          = [ x.xpath('string(.)').extract() for x in selector.css('.moment-info dd') ]
        ##
        # small effort to redeem the exact line (which is buried in the css-class)
        # at least two, or we take the fallback
        better_place = selector.css('dd .icon-t').xpath('@class').re('--(..+)')
        if better_place:
            parts['place'] = better_place
        ##
        # and load
        item_loader.add_value(None, parts)
        ##
        #
        item_loader.add_css('body','div.moment-message')
        return item_loader.load_item()
    pass
    

if __name__ == '__main__':
    pass
