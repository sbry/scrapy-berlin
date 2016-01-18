# -*- coding: utf-8 -*-
import scrapy
from scrapy.cmdline import execute
from berlin.items import BerlinItemLoader
##
# parse the time
from datetime import datetime
##
# for extracting the id        
import urlparse



class BvgSpider(scrapy.Spider):
    name = "bvg"
    allowed_domains = ["www.bvg.de"]
    start_urls = (
            'https://www.bvg.de/de/Meine-BVG/Meine-Augenblicke/Alle-Augenblicke',
    )
    def parse(self, content):
        for href in content.css('.moment-table__more > a:nth-child(1)::attr("href")'):
            full_url = content.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_item_page)
        pass
    def parse_item_page(self, response):
        selector = response.css('div.article__body')
        item_loader = BerlinItemLoader(selector = selector)
        ##
        # string(.) is a way to get innerHtml (from stackoverflow)
        # temporary data-structure to do a multi-assign via add_value(None, {})
        parts = { 'url': response.url, 'source_name': self.name }
        parts['place'],raw_time,unwanted,parts['author'],parts['headline'] \
          = [ x.xpath('string(.)').extract() for x in selector.css('.moment-info dd') ]
        ##
        # and parse the url for the source_id
        try:
            parts['source_id'] = urlparse.parse_qs(urlparse.urlparse(response.url).query)['id']
        except(KeyError):
            pass            
        ##
        # parsing time from 17.01.2016 20:00
        parts['time'] = datetime.strptime(raw_time[0], '%d.%m.%Y %H:%M')
        # and add things
        item_loader.add_value(None, parts)
        item_loader.add_css('body','div.moment-message')
        return item_loader.load_item()
    pass
    

