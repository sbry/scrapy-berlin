pushd $(dirname $0)/../
SCRAPY_BVG_RECURSIVE=1 scrapy crawl bvg
popd
