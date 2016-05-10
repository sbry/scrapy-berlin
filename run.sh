##
# settings
pushd $(dirname $0)
source .scraperc
##
# and run the stuff
cmd_begin=$(date +%s)
case $1 in
    usage|"")
        pushd run
        echo "$0"
        ls *{.py,.sh}
        popd
        ;;
    *)
        ##
        # important for the libraries
        export PYTHONPATH=$PWD
        extension="${1##*.}"
        case $extension in
            sh)
                sh run/$1
                ;;
            py)
                python run/$1
                ;;
        esac

esac
cmd_end=$(date +%s)
cmd_duration=$(($cmd_end-$cmd_begin))
echo $(date) "$0 $1  # ${cmd_duration}s" | tee -a messages.log
popd
