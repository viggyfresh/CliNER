######################################################################
#  CliNER - is_cliner_dir_correct.py                                 #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Is CLINER_DIR env variable set up correctly?             #
######################################################################


import os


def back(p):
    return os.path.dirname(p)


def is_cliner_dir_correct():

    '''
    is_clinerdir_set()

    Purpose: tests if the second line of $CLINER_DIR/README.rst is "CliNER"

    @return boolean indicating whether CLINER_DIR variable is set correctly
    '''

    # Is CLINER_DIR set?
    base = os.getenv('CLINER_DIR')
    if (base == None) or (base == ''):
        return False

    # Is CLINER_DIR set correctly?
    actual_cliner_dir = back(back(back(os.path.abspath(__file__))))
    return base == actual_cliner_dir


if __name__ == '__main__':
    exit(not is_cliner_dir_correct())
