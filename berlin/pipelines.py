# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
##
# for exporting to wordpress
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts,users
import pickle
class PostWordpressPipeline(object):
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
        if(os.path.exists(wp_filename)):
            with open(wp_filename) as fh:
                post = pickle.load(fh)
                fh.close()
                if True:
                    post.date = item['time']
                    self.client.call(posts.EditPost(post.id, post))
            pass
        else:
            try:
                os.makedirs(os.path.dirname(wp_filename))
            except OSError:
                pass
            post = WordPressPost()
            post.title = item['headline']
            post.content = item['body']
            post.terms_names = {
                'category': [item['source_name'].title()],
                'post_tag': [item['place'].title()]
            }
            post.link = item['url']
            post.date = item['time']
            ##
            # @todo we have to create a user if necessary
            # <WordPressUser: max>
            # post.user = self.client.call(users.GetUserInfo())
            post.post_status = 'publish'
            post.id = self.client.call(posts.NewPost(post))
            with open(wp_filename, 'w') as fh:
                pickle.dump(post, fh)
                fh.close()
            pass
        return item
        pass
    pass
##
# For the local saving as rss-fragment
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
    def open_spider(self, spider):
        pass
    def close_spider(self, spider):
        pass
    def process_item(self, item, spider):
        ##
        # need this namespace
        dc = ElementMaker(	nsmap={'dc' : "http://purl.org/dc/elements/1.1/"})
        ##
        # ah python: good to be back
        xml = E.item(
            E.link(item['url']),
            E.guid(item['url'], is_permalink='false'),
            E.pubDate(item['time'].strftime("%a, %d %b %Y %H:%M:%S %z")),
            E.title("%s %s: %s"%(item['source_name'].title(), item['place'].title(), item['headline'])),
            dc.creator(item['author']),
            ##
            # the categories are mostly not printed in the rss-reader,
            # which is why we prepend to body as well
            E.category(item['source_name']),
            E.category(item['place'], domain='place'),
            E.category(item['time'].strftime("%d.%m.%Y"), domain='date'),
            E.description("%s %s"%(item['time'].strftime("%d.%m.%Y"),
                                    item['body']))
        )
        ##
        # for now we just always write the file since it might be an update
        xml_filename = item.filename('xml')
        if(os.path.exists(xml_filename)):
            pass
        else:
            try:
                os.makedirs(os.path.dirname(xml_filename))
            except OSError:
                pass
            with open(xml_filename, 'w') as fh:
                fh.write(etree.tostring(xml, pretty_print=True))
                fh.close()
        return item
