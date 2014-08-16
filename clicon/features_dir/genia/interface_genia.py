######################################################################
#  CliCon - clicon_genia_interface.py                                #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Provide a way for Python to utilize the output of the    #
#               GENIA Tagger                                         #
#                                                                    #
#  Genia Tagger: http://www.nactem.ac.uk/tsujii/GENIA/tagger/        #
######################################################################



__author__ = 'Willie Boag'
__date__   = 'Jan. 27, 2014'

import os
import sys
from commands import getstatusoutput




def genia(geniatagger, data):

    '''
    genia()

    Purpose: Call the genia tagger and return its output in python format

    @param geniatagger.  A path to the executable geniatagger
    @param data.         A list of list of strings (lines of words from a file)
    @return              A list of dcitionaries of the genia tagger's output.
    '''

    # write list to file and then feed it to GENIA
    genia_dir = os.path.dirname(geniatagger)
    tmp_out = os.path.join(genia_dir,'clicon_genia_tmp_file.txt')
    with open(tmp_out, 'w') as f:
        for line in data: f.write(' '.join(line) + '\n')


    # Run genia tagger
    print '\t\tRunning GENIA tagger'
    genia_dir = os.path.dirname(geniatagger)
    stream= getstatusoutput('cd %s ; ./geniatagger -nt %s' % (genia_dir,tmp_out))


    # Process each line of output
    # NOTE: Skips the first four lines of genia tagger output ("loading...")
    retlist = []
    i = 0
    j = 0
    fline = []
    old = []
    for line in stream[1].split('\n')[4:]:

        line = line.split()

        # Empty line
        if line == []: continue

        # One dictionary per word in the file
        output = {'GENIA-word'    :line[0],
                  'GENIA-stem'    :line[1],
                  'GENIA-POS'     :line[2],
                  'GENIA-chunktag':line[3],
                  'GENIA-NEtag'   :line[4]}


        # Add token to list
        fline.append(output)
        j += 1
        if j == len(data[i]):
            i += 1
            j = 0
            retlist.append(fline)
            fline = []

    
    # Remove temp file
    os.remove(tmp_out)


    return retlist




if __name__ == '__main__':
    main()
