# -*- coding: utf-8 -*-
import scrapy
from scrapy.cmdline import execute
from berlin.items import BerlinItem



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
        item = BerlinItem()
        content = response.css('div.article__body')
        # way to get innerHtml
        parts = [x.xpath('string(.)').extract() for x in content.css('.moment-info dd')]
        (item['place'],item['time'], x, item['author'], item['headline']) = parts
        item['body'] = content.css('div.moment-message').extract();
        item['url'] = response.url;
        return item
    pass
    

