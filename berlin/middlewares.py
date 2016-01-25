
from berlin.items import BerlinItem
from scrapy.exceptions import IgnoreRequest
import logging
import os
class NotAgainMiddleware():
    def process_request(self, request, spider):
        """in request.meta it must be defined time source_id and source_name"""
        if all (k in request.meta for k in ("source_name","source_id", "time")):
            i = BerlinItem({k:v for k,v in request.meta.iteritems() if k in BerlinItem.fields})
            if(os.path.exists(i.filename())):
                logging.log(logging.WARNING, "Ignoring URL %s"%request.url)
                raise IgnoreRequest()
        return None;


