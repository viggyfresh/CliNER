#
#  Willie Boag
#
#  CliNER - build_cliner.sh
#



# Installation log
BUILD_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
log="$BUILD_DIR/log_installation.txt"
echo "" > $log
echo -e "\nSee python dependency details at: \n\t$BUILD_DIR/log_installation.txt\n"



# Install 'cliner' script for command line usage
echo "Building executable 'cliner' script"
python setup.py install &> $log
if [[ $? == "0" ]] ; then
    echo -e "'cliner' script built\n"
else
    echo -e "ERROR: cliner setup failed (see log)\n"
fi

