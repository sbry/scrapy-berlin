# -*- coding: utf-8 -*-
##
#
import os, scrapy, glob, sys, pickle
import berlin.pipelines as pipelines
##
#
if __name__ == '__main__':   
    pp = pipelines.WriteRssPipeline()
    for item in pipelines.PicklePipeline.unpickled_items():
        pp.process_item(item,{})
    


 
     
