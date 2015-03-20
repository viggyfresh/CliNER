######################################################################
#  CliNER - clinerdir.py                                             #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Is CLINER_DIR env variable set up correctly?             #
######################################################################


import os


def is_clinerdir_set():

    '''
    is_clinerdir_set()

    Purpose: tests if the second line of $CLINER_DIR/README.rst is "CliNER"

    @return boolean indicating whether CLINER_DIR variable is set correctly
    '''

    # Is CLINER_DIR set?
    base = os.getenv('CLINER_DIR')
    if base == None:
        return False

    # Is CLINER_DIR set correctly?
    path = os.path.join(base, 'README.rst')
    with open(path, 'r') as f:
        lines = f.readlines()
        if len(lines) < 2: return False
        return lines[1].strip() == 'CliNER'



def main():
    if not is_clinerdir_set():
        print '\nERROR: CLINER_DIR not set correctly'
        print '\tthis should be set to path of cloned github directory'
        print "\tex. 'export CLINER_DIR=/home/wboag/CliNER'\n"
    else:
        print '\ngood: CLINER_DIR set correctly\n'



if __name__ == '__main__':
    main()
