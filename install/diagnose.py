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
    if all(status):
        print '\ngood: all Python dependencies installed'
    if status[0] == False:
        print '\nWARNING: Auxillary Python dependencies NOT installed'
        dependencies.display_status(dependencies.auxiliary)
    if status[1] == False:
        print '\nERROR: Required Python dependencies NOT installed'
        dependencies.display_status(dependencies.required)
    if status[2] == False:
        print '\nERROR: Required nltk data NOT downloaded'
        dependencies.display_status(dependencies.nltk_data)
    print


    # 3. GENIA Tagger (optional)


    # 4. UMLS tables (optional)




if __name__ == '__main__':
    main()
