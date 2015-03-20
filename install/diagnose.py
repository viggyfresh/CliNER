######################################################################
#  CliNER - diagnose.py                                              #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Determine if user is missing anything for installation.  #
######################################################################


import os

from cliner_dir import is_clinerdir_set
import dependencies



def main():


    # 1. CLINER_DIR environment variable
    if not is_clinerdir_set():
        print '\nERROR: CLINER_DIR not set correctly'
        print '\tthis should be set to path of cloned github directory'
        print "\tex. 'export CLINER_DIR=/home/wboag/CliNER'\n"
    else:
        print '\ngood: CLINER_DIR set correctly\n'


    # 2. Python dependencies
    status = dependencies.check_python_dependencies_installed()
    if status == 0:
        print '\ngood: all Python dependencies installed'
    elif status == 1:
        print '\nWARNING: Auxillary Python dependencies NOT installed'
        dependencies.display_status(dependencies.auxiliary)
    else:
        print '\nERROR: Required Python dependencies NOT installed'
        dependencies.display_status(dependencies.required)
    print


    # 3. GENIA Tagger


    # 4. UMLS tables




if __name__ == '__main__':
    main()
