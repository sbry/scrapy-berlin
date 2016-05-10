# -*- coding: utf-8 -*-
# #
#
import os, scrapy, glob, sys, json
import subprocess
import cPickle as pickle
import berlin.pipelines as pipelines
from berlin.items import BerlinItem


if __name__ == '__main__':
    pp = pipelines.AugmentBerlinStreetsPipeline()
    for item in pipelines.PicklePipeline.unpickled_items():
        pp.process_item(item, {})

    
    
    


 
     
