# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

##
#
from scrapy.exceptions import DropItem
import os
##
# Life is tough w/o the E
from lxml import etree
from lxml.builder import E, ElementMaker
##
#
class WriteRssItemPipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
    def open_spider(self, spider):
        pass
    def close_spider(self, spider):
        pass
    def process_item(self, item, spider):
        """
        build an item's xml like in rss
    <item>
		<title></title>
		<link></link>
		<pubDate>Mon, 18 Jan 2016 08:00:00 +0000</pubDate>
		<dc:creator></dc:creator>
				<category></category>
		<guid isPermaLink="false"></guid>
		<description></description>
	</item>
        """
        ##
        # need this namespace
        dc = ElementMaker(	nsmap={'dc' : "http://purl.org/dc/elements/1.1/"})
        ##
        # for now we just always write the file since it might be an update
        filename = os.path.join('../scrapy-berlin-results',
                                item['time'].strftime('%Y/%m/%d'),
                                '-'.join(
                                    (item['source_name'],
                                    item['source_id']))) + '.xml'
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass
        ##
        # ah python: good to be back
        xml = E.item(
            # most important
            E.link(item['url']),
            E.guid(item['url'], is_permalink='false'),
            E.pubDate(item['time'].strftime("%a, %d %b %Y %H:%M:%S %z")),
            E.title(item['headline']),
            dc.creator(item['author']),
            ##
            # the categories are mostly not printed in the rss-reader,
            # which is why we prepend to body as well
            E.category(spider.name),
            E.category(item['place'], domain='place'),
            E.category(item['time'].strftime("%d.%m.%Y"), domain='date'),
            E.description(" ".join((spider.name, item['place'], item['time'].strftime("%d.%m.%Y"), item['body'])))
        )
        with open(filename, 'w') as item_file:
            item_file.write(etree.tostring(xml, pretty_print=True))
        return item
