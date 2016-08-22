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
            parts = {}
            source_url = content.urljoin(href.extract())
            parts['source_url'] = source_url
            parts['source_id'] = url_query_parameter(source_url, 'id')
            parts['source_name'] = self.name
            # <div class="">24.01.2016 um 17:00 Uhr • Peterpower</div>
            pub_date = content.css('.moment-table__datetime::text').extract_first().partition(' Uhr')[0]
            parts['time'] = datetime.strptime(pub_date , "%d.%m.%Y um %H:%M")
            # here
            request = scrapy.Request(source_url, callback = self.parse_item_page)
            request.meta['parts'] = parts
            yield request
        ##
        # and open the next page
        if os.getenv('SCRAPY_BVG_RECURSIVE', False):
            next_page = content.css('a.paging__control--next::attr("href")').extract_first()
            logging.log(logging.INFO, "Recursing into next page %s" % next_page)
            yield scrapy.Request(next_page, callback = self.parse)
        pass
    def parse_item_page(self, response):
        selector = response.css('div.article__body')
        item_loader = BerlinItemLoader(selector = selector)
        ##
        # the simple parts
        parts = response.meta['parts']
        place_from_text, raw_time, unwanted, author, headline \
          = [ x.xpath('string(.)') for x in selector.css('.moment-info dd') ]
        parts['author'] = author.extract_first()
        if not 'author' in parts:
            parts['author'] = "-"
        parts['headline'] = headline.extract_first()
        ##
        
        parts['place'] = self.parse_item_page_place(selector)
        ##
        # and load
        item_loader.add_value(None, parts)
        ##
        #
        item_loader.add_css('body','div.moment-message')
        return item_loader.load_item()
    pass
    def parse_item_page_place(self, selector):
        """small effort to redeem the exact line (which is buried in the css-class)
        at least two, or we take the fallback. Like S46"""
        ##
        # input
        # <span class="icon-t icon-t--re 3"><span class="icon-t__line"><span class="visuallyhidden">Bahn</span></span></span>
        # <span class="icon-t icon-t--t"><span class="icon-t__type"><span class="visuallyhidden">Straßenbahn</span></span></span>
        # <span class="icon-t icon-t--u7"><span class="icon-t__line"><span class="visuallyhidden">U-Bahn</span></span></span>
        place_selector = selector.css('dd .icon-t')
        place_from_css = place_selector.xpath('@class').re_first('--(.+)\s*').strip()
        place_visually_hidden = place_selector.xpath('string()').extract_first().strip()
        place_text = place_selector.xpath('../text()').extract_first().strip()
        ##
        # output s/t like U8 S41 T21 B287 M29 M10 X11 F10 RE1
        ##
        # U8 and S41 are complete
        if place_visually_hidden in ('U-Bahn','S-Bahn',):
            place = place_from_css.upper()
        ##
        # Busses need some doing
        elif place_from_css in ('t','b',):
            if place_text.isdigit():
                place = '%s%s'%(place_from_css.upper(),place_text)
            else:    
                place = place_text
        ##
        # otherwise the text is good (M10)
        else:
            place = place_text
        return place

if __name__ == '__main__':
    pass
