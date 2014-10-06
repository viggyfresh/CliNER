#
# install.sh
#
# Purpose: This is a demo that will install CliCon and it's package dependencies
#
# Note: This does not download/install:
#        1) i2b2 data
#        2) UMLS tables
#


function install_python_dependencies {

    modules=(nltk python-crfsuite nose numpy scipy scikit-learn)
    for m in ${modules[@]} ; do

        #echo -e "\n\nmodule: $m\n\n"

        # Install module if necessary
        python $CLICON_DIR/clicon/is_installed.py $m
        if [[ $? != 0 ]] ; then
            echo "installing $m"
            pip install -U $m &>> $log
            echo -e "$m installation complete\n"
        fi

    done

    # Install nltk data
    echo "downloading nltk data"
    python -m nltk.downloader maxent_treebank_pos_tagger wordnet punkt &>> $log
    echo -e "nltk download complete\n"

}



function get_genia {
    # save current path
    old_path=$(pwd)

    # Get sources
    cd $CLICON_DIR/clicon/features_dir/genia
    wget http://www.nactem.ac.uk/tsujii/GENIA/tagger/geniatagger-3.0.1.tar.gz &>> $log
    tar xzvf geniatagger-3.0.1.tar.gz &>> $log
    rm geniatagger-3.0.1.tar.gz

    # Build GENIA tagger
    cd geniatagger-3.0.1/
    echo "$(sed '1i#include <cstdlib>' morph.cpp)" > morph.cpp # fix build error
    echo "building GENIA tagger"
    make &>> $log
    echo -e "GENIA tagger built\n"

    # Successful build ?
    if ! [[ $? -eq 0 ]] ; then
        echo "there was a build error in GENIA"
        return
    fi

    # Set config file location of tagger
    if [[ ! -f "$CLICON_DIR/config.txt" ]] ; then
        echo -e "\tWarning: Could not update config.txt because CLICON_DIR must be an absolute path\n"
        cd $old_path
        return
    fi
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

        echo -e "\n\tYou must define the CLICON_DIR evironment variable to run this script"
        echo -e   "\tRecommendation: 'cd' to the directory containing this script and execute 'export CLICON_DIR=\$(pwd)'\n"

    else

        # Installation log
        log="$CLICON_DIR/installation_log.txt"


        # Create virtual environment
        echo "creating virtual environment"
        virtualenv venv_clicon --system-site-packages &>> $log
        source venv_clicon/bin/activate
        echo -e "virtual environment enabled\n"


        # Install python dependencies
        install_python_dependencies


        # Download & install GENIA tagger
        get_genia


        # Install 'clicon' script for command line usage
        setup_output="setup_output.txt"
        echo "Building executable 'clicon' script"
        python setup.py install &> $setup_output
        success=$?
        echo -e "'clicon' script built\n"


        # Successful
        if [[ $success == 0 ]] ; then
            echo "CliCon successfully installed"
        else
            echo -e "CliCon installation failure\n"
            echo "---------------------FAILURE-------------------------"
            cat $setup_output
            echo "-----------------------------------------------------"
        fi


        cat $setup_output >> $log
        rm $setup_output

    fi

else

    echo -e "\n\tError: Not all resources available on system."
    echo -e "\nPlease ensure the following packages are installed:"

    packages=(g++ gfortran python-dev python-pip python-virtualenv libopenblas-dev liblapack-dev)
    for p in ${packages[@]} ; do
        echo -e "\t$p"
    done
    echo ""

fi
