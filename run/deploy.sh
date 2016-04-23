
RSYNC_OPTIONS='-avhc --exclude=*.pyc --exclude=.* --exclude=*.log'
rsync $RSYNC_OPTIONS ./ $SCRAPY_SSH:$SCRAPY_ROOT
