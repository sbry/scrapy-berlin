##
# we read a file, change the place and output again. 
# import sys,os,re,fileinput; [sys.stdout.write(re.sub('at','op',j)) for j in fileinput.input([f for f in os.listdir('.') if not os.path.isdir(f)],inplace=1)]
##
# and in perl
# find . -type f -name 'polizei-*.xml' | xargs perl -pi -e 's/(<category domain="place">)Berlin\s*/$1/g'
##
# find . -type f -name 'polizei-*.xml' | xargs perl -pi -e 's/(<category domain="place">)([\S]+)\s+-\s+([\S]+)</$1$2-$3</g'
##
# but as always stackoverflow has a point
# find "$path" -type f -print0 | xargs -0 perl -p -i -e "s/term/differenterm/g;"
# find . -type f -name 'bvg-*.xml' | xargs perl -pi -e 's/(<category domain="place">)bBus([^<])+/$1Bus B$2/g'
# find . -type f -name 'bvg-*.xml' | xargs perl -pi -e 's/(<category domain="place">)bExpress-Bus([^<])+/$1Express-Bus $2/g'
# find . -type f -name 'bvg-*.xml' | xargs perl -pi -e 's/(<category domain="place">)bNachtbus([^<])+/$1Nachtbus $2/g'
# find . -type f -name 'bvg-*.xml' | xargs perl -pi -e 's/(<category domain="place">)tStra&#223;enbahn([^<])+/$1Stra&#223;enbahn $2/g'
# find . -type f -name 'bvg-*.xml' | xargs perl -pi -e 's/(<category domain="place">)mt([^<])+/$1MetroTram $2/g'
# find . -type f -name 'bvg-*.xml' | xargs perl -pi -e 's/(<category domain="place">)mb([^<])+/$1MetroBus $2/g'
# find . -type f -name 'bvg-*.xml' | xargs perl -pi -e 's/(<category domain="place">)fF&#228;hre([^<])+/$1F&#228;hre $2/g'
