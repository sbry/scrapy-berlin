# -*- coding: utf-8 -*-
import scrapy
import re
import logging
from radio.items import RadioItem
class SomaSpider(scrapy.Spider):
    name = "soma"
    allowed_domains = ["somafm.com"]
    start_urls = (
        'http://somafm.com/',
    )
    def parse(self, response):
        for station_link_element in response.css('.cbshort>a::attr("href")'):
            pls_link = re.sub('/$', '.pls', station_link_element.extract())
            logging.log(logging.DEBUG, pls_link)
            yield scrapy.Request('http://somafm.com%s'%pls_link, callback = self.parse_pls)
        pass
    def parse_pls(self, response):
        """pls-files are strange we just need a url"""
        item = RadioItem()
        urls = re.findall('http.+\n', response.body, re.M)
        ##
        # use the last url preferrably it has the name of the station in the url
        item['url'] = urls.pop()
        ##
        # all the titles are the same
        titles = re.findall('Title1=(.*)\n', response.body, re.M)
        item['name'] = titles.pop()
        yield item
    pass

