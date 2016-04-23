# -*- coding: utf-8 -*-
##
# this is seriously not the best way
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts,users
import os, pickle
def wp_truncate():
    client = Client(os.getenv('SCRAPY_WP_RPCURL'),
                    os.getenv('SCRAPY_WP_USERNAME'),
                    os.getenv('SCRAPY_WP_PASSWORD'))
    while 1:
        posts_slice = client.call(posts.GetPosts())
        if len(posts_slice):
            for p in posts_slice:
                print p.id
                client.call(posts.DeletePost(p.id))
        else:
            break

if __name__ == '__main__':
    wp_truncate()
