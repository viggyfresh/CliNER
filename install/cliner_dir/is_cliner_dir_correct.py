######################################################################
#  CliNER - is_cliner_dir_correct.py                                 #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Is CLINER_DIR env variable set up correctly?             #
######################################################################


import os


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
    path = os.path.join(base, 'README.rst')
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
            if len(lines) < 2: return False
            return lines[1].strip() == 'CliNER'
    except IOError:
        return False


if __name__ == '__main__':
    exit(not is_cliner_dir_correct())
