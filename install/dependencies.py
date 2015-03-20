######################################################################
#  CliNER - dependencies.py                                          #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Determine which python modules are installed.            #
######################################################################


import sys



# Modules used by cliner (package name -> module name)
required = {
             'scipy'           : 'import scipy'      ,
             'numpy'           : 'import numpy'      ,
             'nltk'            : 'import nltk'       ,
             'python-crfsuite' : 'import pycrfsuite' ,
             'scikit-learn'    : 'from sklearn.feature_extraction  import DictVectorizer'
           }

auxiliary = {
             'marisa-trie' : 'import marisa_trie'    ,
             'nose'        : 'import nose'
            }



def main():

    # Output package statuses
    print '\nREQUIRED'
    display_status(required)

    print '\nAUXILIARY'
    display_status(auxiliary)
    print




def display_status(module2import):
    ''' Iterate through dictionary and display in pretty format '''
    installed = status_report(module2import)
    print '\t|  module-name  |   status    |'
    print '\t|' + '-'*15 + '|' + '-' * 13 + '|'
    for module in installed.keys():
        if installed[module]:
            print '\t|%-15s|  installed  |' % module
        else:
            print '\t|%-15s|    ERROR    |'   % module



def status_report(module2import):

    '''
    status_report()

    Purpose: Determine which modules can be successfully imported

    @param module2import. Dictionary mapping python-module-name to code-to-import
    @param <dictionary> mapping python-module-name to boolean
    '''

    installed = {}

    for module in module2import.keys():

        # Attempt to import module
        try:
            # Get import statement from module name
            attempt = module2import[module]

            # Execute import
            exec(attempt)
            installed[module] = True
        except ImportError:
            installed[module] = False

    return installed



def check_python_dependencies_installed():

    '''
    check_python_dependencies_installed()

    Purpose: Determine whether all necesarry python modules are installed

    @return either 0, 1, or 2:
            0 <- everything is installed
            1 <- missing some auxiliary modules
            2 <- missing some required modules
    '''

    # Missing required modules?
    required_modules = status_report(required)
    if not all(required_modules.values()):
        return 2

    # Missing auxiliary modules?
    auxiliary_modules = status_report(auxiliary)
    if not all(auxiliary_modules.values()):
        return 1

    # Successful
    return 0



if __name__ == '__main__':
    main()
