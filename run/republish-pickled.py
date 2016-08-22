# -*- coding: utf-8 -*-
##
#
import os, scrapy, glob, sys, pickle 
import berlin.pipelines as pipelines
##
#
if __name__ == '__main__':
    pp = pipelines.PublishPipeline.from_crawler({})
    pp.open_spider({})
    for pickle_filename in glob.glob(os.getenv('SCRAPY_DATADIR', '../scrapy-items') + '/*.p'):
        with open(pickle_filename, 'r') as fh:
            item = pickle.load(fh)
            fh.close()
        pp.process_item(item,{})
    


 
     
