# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os, pickle
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts, users
import cmd
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

import glob, json, subprocess
def read_berlin_streets():
    """in every file there is a json-list of streets, we just need a flat list"""
    pattern = os.getenv('SCRAPY_ROOT', '.') + '/../streetname-scraper/data/*.json'
    for f in glob.glob(pattern):
        with open(f) as fh:    
            # flatten the lists
            for street in json.load(fh):
                # like go: _ is thowaway
                street['district'], _ = os.path.splitext(os.path.basename(f))
                yield street 
            fh.close()
def match_street(item, street):
        """match a single street this whole thing takes forever"""
        cmd = match_street_cmd(item, street)
        # print cmd
        return not(subprocess.call(cmd))
def match_street_helper(args):
    return match_street(*args)
def match_street_cmd(item, street):
    disjunction = list()
    # partial matching is better for now, half the string or at least 5 letters
    disjunction.append(re.escape(street[u'title'][:max((len(street[u'title']) / 2), 13)]))
    filename = item.filename('xml')
    return ['/usr/bin/grep', '-qEi', '(' + '|'.join(disjunction) + ')', filename]
# #
#
from items import BerlinItem
import re

class AugmentBerlinStreetsPipeline():
    """the plan is to match streets"""
    # #
    # takes a long time we try to limit it to once per session
    streets = list(read_berlin_streets())
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
    def open_spider(self, spider):
        pass
    def close_spider(self, spider):
        pass
    def process_item(self, item, spider):
        """we grep on a file to decide if a street matches, 
        if it does we write it into a new datastructure which 
        we save in a separate directory"""
        # benchmarks are clear, matching simple takes 44s per item and 16 with the 
        # number of processes = number of cpu 
        # and 17 with the number of processes = number of cpu * 2
        if False:
            matched_streets = self.process_item_match_streets_simple(item)
        else:
            matched_streets = self.process_item_match_streets_pooled(item)
        self.process_item_match_streets_save(item, matched_streets)
        return item
    def process_item_match_streets_simple(self, item):
        matched_streets = list()
        for street in self.streets:
            if match_street(item, street):
                matched_streets.append(street)
        return matched_streets
    def process_item_match_streets_pooled(self, item):
        import multiprocessing
        # seems the ideal value
        processes = multiprocessing.cpu_count()
        p = multiprocessing.Pool(processes=processes)
        boolean_matches = p.map(match_street_helper, [(item, street,) for street in self.streets])
        # we need to return those streets where the grep returned true
        # first time i use zip: quite a success
        return [street for street, matched in zip(self.streets, boolean_matches) if matched]
    def process_item_match_streets_save(self, item, matched_streets):
        if(not len(matched_streets)):
            return True;
        pickle_filename = item.filename('p1')
        try:
            os.makedirs(os.path.dirname(pickle_filename))
        except OSError:
            pass
        with open(pickle_filename, 'w') as fh:
            pickle.dump(list(matched_streets), fh)
            fh.close()
    @classmethod
    def filenames(cls):
        """p1 for the first pickled augmentation"""
        return glob.glob(os.getenv('SCRAPY_DATADIR') + '/p1/*.p1')
    pass

if __name__ == '__main__':
    pass
