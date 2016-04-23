##
# one-time-reimport from django-dump of 2011-2014
pushd $(dirname $0)/../
scrapy crawl stag
popd
