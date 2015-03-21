#
# Willie Boag            wboag@cs.uml.edu
#
# CliNER - set_cliner_dir.sh
#
# NOTE: Must be run with 'source'
#

# Determine if current CLINER_DIR is set properly
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
python $DIR/is_cliner_dir_correct.py
is_setup=$?

# If not set properly, then set it yourself
if [[ $is_setup != "0" ]] ; then
    cliner_dir=$(python $DIR/print_cliner_dir.py)
    export CLINER_DIR="$cliner_dir"
fi
