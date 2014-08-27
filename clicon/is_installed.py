######################################################################
#  CliCon - is_installed.py                                          #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Determine if a given python module is available.         #
######################################################################


import sys



def main():

    # Ensure proper usage
    if len(sys.argv) != 2:
        print '\n\tusage: %s module_name\n' % sys.argv[0]
        exit(2)


    # Modules used by clicon (package name -> module name)
    module2import = { 'scipy'           : 'import scipy'      , 
                      'numpy'           : 'import numpy'      , 
                      'nose'            : 'import nose'       ,
                      'nltk'            : 'import nltk'       ,
                      'python-crfsuite' : 'import pycrfsuite' ,
                      'scikit-learn'    : 'from sklearn.feature_extraction  import DictVectorizer' }


    # Attempt to import module
    try:
        # Get import statement from module name
        if sys.argv[1] not in module2import: exit(3)
        attempt = module2import[ sys.argv[1] ]

        # Execute import
        exec(attempt)
        error = 0
    except ImportError:
        error = 1


    # Return error code back to shell
    exit(error)



if __name__ == '__main__':
    main()
