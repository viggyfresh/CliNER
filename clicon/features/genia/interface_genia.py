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


def main():

    f = open('/home/wboag/ConceptExtraction-master/data/concept_assertion_relation_training_data/beth/txt/record-20.txt', 'r')

    txt = f.readlines()

    data = []
    for line in txt:
        data.append(line.split())

    tagger = '/home/wboag/geniatagger-3.0.1/geniatagger'
    for (line,linedict) in zip(txt,genia(tagger,data)):
       print line.split(), '\n'
       for d in linedict:
           print d
       print '---\n\n'



#
#  genia()
#
#  Call the genia tagger and return its output in python format
#
def genia(geniatagger, data):

    '''
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
    stream = getstatusoutput('cd %s ; ./geniatagger -nt %s' % (genia_dir,tmp_out))


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
            #print data[i]
            #print fline
            #print '---'
            i += 1
            j = 0
            retlist.append(fline)
            fline = []

    
    # Remove temp file
    os.remove(tmp_out)


    return retlist




if __name__ == '__main__':
    main()
