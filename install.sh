#
# install.sh
#
# Purpose: This is a demo that will install CliCon and it's package dependencies
#
# Note: This does not download/install:
#        1) i2b2 data
#        2) UMLS tables
#


function get_genia {
    # save current path
    old_path=$(pwd)

    # Get sources
    cd $CLICON_DIR/clicon/features/genia
    wget http://www.nactem.ac.uk/tsujii/GENIA/tagger/geniatagger-3.0.1.tar.gz
    tar xzvf geniatagger-3.0.1.tar.gz

    # Build GENIA tagger
    cd geniatagger-3.0.1/
    echo "$(sed '1i#include <cstdlib>' morph.cpp)" > morph.cpp # fix build error
    make

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




# Create virtual environment
virtualenv venv_clicon
source venv_clicon/bin/activate




# CLICON_DIR must be defined before proceeding
if [[ "$CLICON_DIR" = "" ]] ; then
    CLICON_DIR="$( cd "$( dirname "$0" )" && pwd )"
    echo -e "\nEnvironment variable CLICON_DIR must be defined."
    echo -e   "Execute the following and re-run install.sh: \n"
    echo -e "\texport CLICON_DIR=\"$CLICON_DIR\""
    echo ""
    exit
fi




# Install python dependencies
easy_install pip simplejson
easy_install simplejson
pip install Flask
pip install nose
pip install -U pyyaml 
python -m nltk.downloader maxent_treebank_pos_tagger
python -m nltk.downloader wordnet

# Install Scikit-Learn (SVM)
pip install numpy 
pip install scikit-learn
pip install scipy

# Install python-crfsuite (CRF)
pip install python-crfsuite




# Download & install GENIA tagger
get_genia




# Install 'clicon' CLI command
python setup.py install
