######################################################################
#  CliCon - format.py                                                #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Script to convert i2b2 <-> xml data format               #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Jul. 3, 2014'



import argparse
import sys
import os
import glob

import helper
import note




def create_filename(odir, bfile, extension):
    fname = os.path.basename(bfile) + extension
    return os.path.join(odir,fname)



def main():

    # Argument Parser
    parser = argparse.ArgumentParser()

    parser.add_argument("-t",
        dest = "txt",
        help = "The files that contain the training examples",
    )

    parser.add_argument("-c",
        dest = "con",
        help = "The files that contain the labels for the training examples",
    )

    parser.add_argument("-x",
        dest = "xml",
        help = "The files that contain the aml-annotated data",
    )

    parser.add_argument("-o",
        dest = "out",
        default = None,
        help = "Directory to output data",
    )

    parser.add_argument("-f",
        dest = "format",
        help = "Output format (i2b2 or xml?)",
    )

    # Parse the command line arguments
    args = parser.parse_args()


    # Parse arguments
    txt      = args.txt
    con      = args.con
    xml      = args.xml
    out_file = args.out
    format   = args.format


    # Ensure format is specified
    if (not format) or ((format != 'xml') and (format != 'i2b2')):
        print >>sys.stderr, '\n\tError: Must specify output format (i2b2 or xml)'
        print >>sys.stderr, ''
        exit(1)

    # Cannot have ambiguous input
    if (txt and con) and xml:
        print >>sys.stderr, '\n\tError: Input must be either (i2b2) XOR (xml)\n'
        exit(2)

    # If insufficient data is given (must have txt+con OR xml)
    if (not (txt and con)) and (not xml):
        print >>sys.stderr, '\n\tError: Must supply either:'
        print >>sys.stderr,   '\t         1) i2b2 txt & con file'
        print >>sys.stderr,   '\t         2) xml file\n'
        exit(3)


    # Read input data into note object
    N = note.Note()
    if xml:
        N.read_xml(xml)
    else:
        N.read_i2b2(txt, con)
 

    # Where to output data
    if out_file:
        out_f = open(out_file, 'w')
    else:
        out_f = sys.stdout

        
    # Desired output format
    if format == 'xml':
        out = N.write_xml()
    else:
        # i2b2 format
        out = N.write_i2b2()

    # Output data
    out_f.write(out)


    # Close output file
    if out_file:
        out_f.close()



if __name__ == '__main__':
    main()
