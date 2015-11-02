#
#  Willie Boag         wboag@cs.uml.edu
#
#  CliNER - create_virtualenv.sh
#
#  NOTE: Must be run with 'source'
#


# Virtual Environment?
if [[ ! $VIRTUAL_ENV ]] ; then

    # Exists?
    if [[ -f $CLINER_DIR/venv_cliner ]] ; then
        source $CLINER_DIR/venv_cliner/bin/activate
    else
        old=$(pwd)
        cd $CLINER_DIR
        virtualenv --python=python2.7 venv_cliner > /dev/null
        source venv_cliner/bin/activate
        cd $old
    fi

fi

