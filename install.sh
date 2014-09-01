#
# install.sh
#
# Purpose: This is a demo that will install CliCon and it's package dependencies
#
# Note: This does not download/install:
#        1) i2b2 data
#        2) UMLS tables
#



# Installation log
BASE_DIR="$( cd "$( dirname "$0" )" && pwd )"
log="$BASE_DIR/installation_log.txt"


function install_python_dependencies {

    modules=(nltk python-crfsuite nose numpy scipy scikit-learn)
    for m in ${modules[@]} ; do

        #echo -e "\n\nmodule: $m\n\n"

        # Install module if necessary
        python $CLICON_DIR/clicon/is_installed.py $m
        if [[ $? != 0 ]] ; then
            echo "installing $m"
            pip install -U $m >> $log
        fi

    done

    # Install nltk data
    echo "downloading nltk data"
    python -m nltk.downloader maxent_treebank_pos_tagger wordnet >> $log

}



function get_genia {
    # save current path
    old_path=$(pwd)

    # Get sources
    cd $CLICON_DIR/clicon/features_dir/genia
    wget http://www.nactem.ac.uk/tsujii/GENIA/tagger/geniatagger-3.0.1.tar.gz >> $log
    tar xzvf geniatagger-3.0.1.tar.gz
    rm geniatagger-3.0.1.tar.gz

    # Build GENIA tagger
    cd geniatagger-3.0.1/
    echo "$(sed '1i#include <cstdlib>' morph.cpp)" > morph.cpp # fix build error
    make >> $log

    # Successful build ?
    if ! [[ $? -eq 0 ]] ; then
        echo "there was a build error in GENIA"
        return
    fi

    # Set config file location of tagger
    config_file="$CLICON_DIR/config.txt"
    out_tmp="out.tmp.txt"
    echo "GENIA $(pwd)/geniatagger" > $out_tmp
    while read line ; do
        if ! [[ $line = GENIA* ]] ; then
            echo $line >> $out_tmp
        fi
    done < "$config_file"
    mv $out_tmp $config_file

    # return to original path
    cd $old_path
}



# Ensure resources are available
which g++ gfortran virtualenv pip &> /dev/null
resources=$?
if [[ $resources -eq 0 ]] ; then


    # CLICON_DIR must be defined before proceeding
    if [[ "$CLICON_DIR" = "" ]] ; then
        export CLICON_DIR=$BASE_DIR
        echo -e "export CLICON_DIR=$CLICON_DIR" >> .bashrc

    fi


    # Create virtual environment
    virtualenv venv_clicon --system-site-packages
    source venv_clicon/bin/activate


    # Install python dependencies
    install_python_dependencies


    # Download & install GENIA tagger
    get_genia


    # Install 'clicon' script for command line usage
    setup_output="setup_output.txt"
    python setup.py install > $setup_output


    # Successful
    if [[ $? == 0 ]] ; then
        echo "CliCon successfully installed"
    else
        echo "CliCon installation failure"
        cat $setup_output
    fi


    cat $setup_output >> $log
    rm $setup_output


else

    echo -e "\n\tError: Not all resources available on system."
    echo -e "\nPlease ensure the following packages are installed:"

    packages=(g++ gfortran python-dev python-pip python-virtualenv libopenblas-dev liblapack-dev)
    for p in ${packages[@]} ; do
        echo -e "\t$p"
    done
    echo ""

fi
