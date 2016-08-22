# -*- coding: utf-8 -*-
# #
#
import os, scrapy, glob, sys, json
import berlin.pipelines as pipelines

if __name__ == '__main__':
    streets = pipelines.read_berlin_streets()
    with open('streets.json', 'wb') as fh:
        json.dump(list(streets), fh)  
        fh.close()


    
    
    


 
     
