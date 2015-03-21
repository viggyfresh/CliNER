#
# Willie Boag            wboag@cs.uml.edu
#
# CliNER - smart_install.sh
#
# NOTE: Must be run with 'source'
#

# 'install' directory
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# set CLINER_DIR variable
source $DIR/cliner_dir/set_cliner_dir.sh

# python dependencies (use source because of virtualenv)
source $DIR/dependencies/install_python_dependencies.sh

# install 'cliner' command
bash $DIR/build/build_cliner.sh

# genia tagger
bash $DIR/genia/install_genia.sh
