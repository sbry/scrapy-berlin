# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os, pickle
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts, users
import cmd, glob
from posix import chdir
# #
#
def get_place_post_tag_names(value):
    return [ word for word in value.split("/") if word ]
class PublishPipeline(object):
    """
    use xmlprc of wordpress to synchronize via push
    """
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
    def open_spider(self, spider):
        self.client = Client(os.getenv('SCRAPY_WP_RPCURL'),
                             os.getenv('SCRAPY_WP_USERNAME'),
                             os.getenv('SCRAPY_WP_PASSWORD'))
        pass
    def close_spider(self, spider):
        pass
    def process_item(self, item, spider):
        wp_filename = item.filename('wp')
        if os.path.exists(wp_filename):
            with open(wp_filename) as fh:
                post = pickle.load(fh)
                fh.close()
                # #
                # Here one might update or fix things
                if False:
                    post.terms_names = {
                        'category': [item['source_name'].title()],
                        'post_tag': get_place_post_tag_names(item['place'])
                    }
                    self.client.call(posts.EditPost(post.id, post))
                    pass
                pass
            pass
        else:
            post = WordPressPost()
            post.title = item['headline']
            try:
                post.content = item['body']
            except KeyError:
                return None
            try:
                item['place']
            except KeyError:
                item['place'] = ""
            post.terms_names = {
                'category': [item['source_name'].title()],
                'post_tag': get_place_post_tag_names(item['place'])
            }
            post.link = item['source_url']
            post.date = item['time']
            post.post_status = 'publish'
            post.id = self.client.call(posts.NewPost(post))
            with open(wp_filename, 'w') as fh:
                pickle.dump(post, fh)
                fh.close()
            pass
        return item
        pass
    pass

import os
import cPickle as pickle
class PicklePipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
    def open_spider(self, spider):
        pass
    def close_spider(self, spider):
        pass
    def process_item(self, item, spider):
        pickle_filename = item.filename('p')
        try:
            os.makedirs(os.path.dirname(pickle_filename))
        except OSError:
            pass
        with open(pickle_filename, 'w') as fh:
            pickle.dump(item, fh)
            fh.close()
        return item
    pass
    @classmethod
    def filenames(cls):
        return glob.glob(os.getenv('SCRAPY_DATADIR') + '/p/*.p')
    @classmethod
    def unpickled_items(cls):
        for pickle_filename in cls.filenames():
            with open(pickle_filename, 'r') as fh:
                item = pickle.load(fh)
                fh.close()
                yield item

# #
# For the local saving as rss-fragment: for text-analysis
from lxml import etree
from lxml.builder import E, ElementMaker
class WriteRssPipeline(object):
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
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
    def close_spider(self, spider):
        pass
    def process_item(self, item, spider):
        # #
        # need this namespace
        dc = ElementMaker(nsmap={'dc' : "http://purl.org/dc/elements/1.1/"})
        # #
        # ah python: good to be back
        xml = E.item(
            E.link(item['source_url']),
            E.guid(item['source_url'], is_permalink='false'),
            E.pubDate(item['time'].strftime("%a, %d %b %Y %H:%M:%S %z")),
            E.title(item['headline']),
            dc.creator(item['source_name']),
            # #
            # the categories are mostly not printed in the rss-reader,
            # which is why we prepend to body as well
            E.category(item['source_name']),
            E.category(item['place'], domain='place'),
            E.category(item['time'].strftime("%d.%m.%Y"), domain='date'),
            E.description(item['body'])
        )
        # #
        # for now we just always write the file since it might be an update
        xml_filename = item.filename('xml')
        with open(xml_filename, 'w') as fh:
            fh.write(etree.tostring(xml, pretty_print=True))
            fh.close()
        return item
    @classmethod
    def filenames(cls):
        return glob.glob(os.getenv('SCRAPY_DATADIR') + '/xml/*.xml')

import subprocess
class AugmentBerlinStreetsPipeline():
    """we match streets with go: it's quicker"""
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
    def open_spider(self, spider):
        pass
    def close_spider(self, spider):
        pass
    def process_item(self, item, spider):
        xml_filename = item.filename('xml')
        dirnames = [os.path.dirname(__file__), '../street-matcher']
        subprocess.call(['./main', xml_filename], cwd="/".join(dirnames))
        return item
    pass

if __name__ == '__main__':
    pass
