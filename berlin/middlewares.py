
from berlin.items import BerlinItem
from scrapy.exceptions import IgnoreRequest
import os, logging
class NotAgainMiddleware():
    def process_request(self, request, spider):
        """in request.meta it must be defined time source_id and source_name"""
        try:
            parts = request.meta['parts']
        except KeyError:
            return None
        if all (k in parts for k in ("source_name","source_id")):
            i = BerlinItem(parts)
            if(os.path.exists(i.filename())):
                logging.log(logging.WARNING, "Ignoring URL %s"%request.url)
                raise IgnoreRequest()
        return None


