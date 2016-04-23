# scrapy-berlin

Scraping two common sources (polizeiberlin, bvg-augenblicke) of
Berlin-News for RSS with [Scrapy](http://www.scrapy.org) 

## Output Pipeline

- update a wordpress-site (via env

```bash
 $SCRAPY_WP_RPCURL 
 $SCRAPY_WP_USERNAME
 $SCRAPY_WP_PASSWORD
```

) with
 [Python Wordpress Xmlrpc](http://python-wordpress-xmlrpc.readthedocs.org/en/latest/)
 
- write the scraped content as a rss-fragment (item) into a file-tree (SCRAPY_XML_BASEDIR/{year}/{source_name}-{source_id}.xml)

- Archives restored via files in STAGGER_IR

## Installation

+ python2. I use 2.7.9 at this point. Right now scrapy does not work with python3 because twisted does not work with python3.
+ pip install -r requirements.txt
+ scrapy crawl bvg; scrapy crawl polizei

