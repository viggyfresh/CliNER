#
# install.sh
#
# Purpose: This is a demo that will install CliCon and it's package dependencies
#
# Usage: 'source install.sh'  (It is important to use 'source', not 'bash')
#
# Note: This does not download/install:
#        1) i2b2 data
#        2) UMLS tables
#



function create_clicon {
    # Create wrapper directory to hold:
    #     1) virtual environment
    #     2) CliCon source from github
    mkdir clicon
    cd clicon

    virtualenv venv_clicon
    source venv_clicon/bin/activate

    git clone https://github.com/mitmedg/CliCon.git
    cd CliCon
    git checkout machine-learning
}



function environ_clicon {
    # Set environment variable (check if it is defined)
    if [[ "$CLICON_DIR" = "" ]] ; then
        echo -e "\n\t"
        echo -e "Appending line to ~/.bashrc to remember environment variable\n"

        echo "export CLICON_DIR=\"$(pwd)/clicon/CliCon\"" >> ~/.bashrc
        source ~/.bashrc
        export CLICON_DIR

    fi

    setup_environ=0
}



function install_clicon {

    # Get python dependencies
    easy_install pip
    easy_install simplejson
    pip install Flask
    pip install nose
    pip install -U pyyaml 

    # Install nltk data
    python -m nltk.downloader maxent_treebank_pos_tagger
    python -m nltk.downloader wordnet


    # apt-get doesn't seem to be working at getting numpy
    pip install numpy scikit-learn scipy python-crfsuite
    setup_dependencies=$?

}



# Get GENIA
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
        setup_genia=1
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


    # Success
    setup_genia=0

    # return to original path
    cd $old_path
}



# Setup 'clicon' command for CLI
function setup {
    cd $CLICON_DIR
    python setup.py install
    setup_install=$?
}



# Base directory cannot exist yet
if [[ -e clicon ]] ; then
    echo -e "\n\tError: Cannot already have a file named 'clicon' in directory\n"
else

    # Install resources
    create_clicon
    environ_clicon
    install_clicon
    get_genia
    setup
        
    echo -e "\n\n"

    # Print installation successes/failures
    if [[ $setup_environ -eq 0 ]] ; then
        echo "Environemt variable confiuration -- SUCCESS"
    else
        echo "Environemt variable confiuration -- FAILURE"
        echo -e "\tSee README for details"
    fi


    if [[ $setup_dependencies -eq 0 ]] ; then
        echo "Install python dependencies      -- SUCCESS"
    else
        echo "Install python dependencies      -- FAILURE"
        echo -e "\tSee README for details"
    fi


    if [[ $setup_genia -eq 0 ]] ; then
        echo "Install GENIA tagger             -- SUCCESS"
    else
        echo "Install GENIA tagger             -- FAILURE"
        echo -e "\tSee README for details"
    fi


    if [[ $setup_install -eq 0 ]] ; then
        echo "Install 'clicon' command for CLI -- SUCCESS"
    else
        echo "Install 'clicon' command for CLI -- FAILURE"
        echo -e "\tSee README for details"
    fi

fi

