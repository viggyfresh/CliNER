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
        default = '.',
        help = "Directory to output data",
    )

    parser.add_argument("-f",
        dest = "format",
        help = "Output format (i2b2 or xml?)",
    )

    # Parse the command line arguments
    args = parser.parse_args()


    # Parse arguments
    txt_f   = args.txt
    con_f   = args.con
    xml_f   = args.xml
    out_dir = args.out
    format  = args.format


    # Ensure format is specified
    if (not format) or ((format != 'xml') and (format != 'i2b2')):
        print >>sys.stderr, '\n\tError: Must specify output format (i2b2 or xml)'
        print >>sys.stderr, ''
        exit(1)

    # Cannot have ambiguous input
    if (txt_f and con_f) and xml_f:
        print >>sys.stderr, '\n\tError: Input must be either (i2b2) XOR (xml)\n'
        exit(2)

    # Ensure proper data is available (equal - AKA if not XOR)
    if (not (txt_f and con_f)) and (not xml_f):
        print >>sys.stderr, '\n\tError: Must supply either:'
        print >>sys.stderr,   '\t         1) i2b2 txt & con file'
        print >>sys.stderr,   '\t         2) xml file\n'
        exit(3)


    # Read input data into note object
    N = note.Note()
    if xml_f:
        basefile = xml_f
        N.read_xml(xml_f)
    else:
        basefile = txt_f
        N.read_i2b2(txt_f, con_f)
 
        
    # Output data in desired format
    if format == 'xml':

        # xml format
        xml_out = N.write_xml()

        # output xml file
        xml_file = create_filename(out_dir, basefile, '.xml')
        output_file(xml_file, xml_out)

    else:

        # i2b2 format
        txt_out = N.write_txt()
        con_out = N.write_i2b2_con()

        # output txt file
        txt_file = create_filename(out_dir, basefile, '.txt')
        output_file(txt_file, txt_out)

        # output con file
        con_file = create_filename(out_dir, basefile, '.con')
        output_file(con_file, con_out)





def create_filename(out_dir, orig_f, new_extension):
    fname = os.path.basename(orig_f)[:-4] + new_extension
    return os.path.join(out_dir, fname)


def output_file(fname, out):
    print 'outputting: ', fname
    with open(fname, 'w') as f:
        print >>f, out



if __name__ == '__main__':
    main()
