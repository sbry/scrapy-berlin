# -*- coding: utf-8 -*-
import scrapy
from scrapy.cmdline import execute
from berlin.items import BerlinItem



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
        item = BerlinItem()
        content = response.css('div.article')
        item['headline'] = content.css('h1.title::text').extract();
        item['time'] = content.css('div.polizeimeldung:nth-child(1)::text').extract();
        item['place'] = content.css('div.polizeimeldung:nth-child(2)::text').extract();
        item['author'] = 'Polizei Berlin'
        # this might be several
        item['body'] = content.css('div.textile').extract();
        item['url'] = response.url;
        return item
    pass
    

