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
            request = scrapy.Request(full_url, callback = self.parse_item_page)
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
        ##
        # and open the next page
        if os.getenv('SCRAPY_BVG_RECURSIVE', False):
            next_page = content.css('a.paging__control--next::attr("href")').extract()[0]
            logging.log(logging.INFO, "Recursing into next page %s" % next_page)
            yield scrapy.Request(next_page, callback = self.parse)
        pass
    def parse_item_page(self, response):
        selector = response.css('div.article__body')
        item_loader = BerlinItemLoader(selector = selector)
        ##
        # the simple parts
        parts = response.meta['parts']
        parts['url'] = response.url
        place_from_text, raw_time, unwanted, author, headline \
          = [ x.xpath('string(.)') for x in selector.css('.moment-info dd') ]
        parts['author'] = author.extract()[0]
        parts['headline'] = headline.extract()[0]
        ##
        # small effort to redeem the exact line (which is buried in the css-class)
        # at least two, or we take the fallback. Like "S46"
        place_from_css = selector.css('dd .icon-t').xpath('@class').re('--(.+)\s*')[0]
        if len(place_from_css) == 1:
            ##
            # OMG Bus is different B240 is what we want
            parts['place'] = "%s%s"%(place_from_css,place_from_text.extract()[0])
        elif len(place_from_css) > 1:
            ##
            # good css-place
            parts['place'] = "%s"%(place_from_css)
        else:
            parts['place'] = place_from_text
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
