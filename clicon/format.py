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
    if args.txt: txt_files = glob.glob(args.txt)
    if args.con: con_files = glob.glob(args.con)
    if args.xml: xml_files = glob.glob(args.xml)
    if args.out: out_dir   =           args.out
    format = args.format


    # Ensure format is specified
    if (not format) or ((format != 'xml') and (format != 'i2b2')):
        print >>sys.stderr, '\n\tError: Must specify output format (i2b2 or xml)'
        print >>sys.stderr, ''
        exit(1)


    # Ensure proper data is available
    if not ((args.txt and args.con) or (args.xml)):
        print >>sys.stderr, '\n\tError: Must supply either:'
        print >>sys.stderr,   '\t         1) i2b2 txt & con files'
        print >>sys.stderr,   '\t         2) xml file\n'
        exit(2)


    if format == 'xml':

        # Group input i2b2 txt/con files together
        txt_files_map = helper.map_files(txt_files)
        con_files_map = helper.map_files(con_files)
        file_list = []
        for k in txt_files_map:
            if k in con_files_map:
                file_list.append((txt_files_map[k], con_files_map[k]))


        # For each matching txt/con pair
        for txt_f,con_f in file_list:

            # i2b2 -> xml
            output = i2b2_to_xml(txt_f, con_f)


            # output file name
            xml_name = os.path.basename(txt_f)[:-4] + '.xml'
            xml_file = os.path.join(out_dir, xml_name)

            # print output xml file
            print 'outputting: ', xml_file
            with open(xml_file, 'w') as f:
                print >>f, output


    else:

        # For each xml file
        for xml_f in xml_files:

            # i2b2 -> xml
            txt_out, con_out = xml_to_i2b2(xml_f)


            # output txt file
            txt_name = os.path.basename(xml_f)[:-4] + '.txt'
            txt_file = os.path.join(out_dir, txt_name)

            print 'outputting: ', txt_file
            with open(txt_file, 'w') as f:
                print >>f, txt_out


            # output con file
            con_name = os.path.basename(xml_f)[:-4] + '.con'
            con_file = os.path.join(out_dir, con_name)

            print 'outputting: ', con_file
            with open(con_file, 'w') as f:
                print >>f, con_out





def i2b2_to_xml(txt, con):

    """
    i2b2_to_xml()

    Purpose: Convert data from i2b2 format to xml format.

    @param txt  A path to the text    file.
    @param con  A path to the concept file.
    @return     A string containing the data in xml format.
    """

    # Read note from i2b2 format
    N = note.Note()
    N.read_i2b2(txt, con)

    # Output note into xml format
    out = N.write_xml()
    return out




def xml_to_i2b2(xml):

    """
    xml_to_i2b2()

    Purpose: Convert data from xml format to i2b2 format.

    @param xml  A file containing xml-annotated data
    @return     A tuple of strings (text_data,concept_data)
    """


    # Read note from xml format
    N = note.Note()
    N.read_xml(xml)

    # Output note into i2b2 format
    txt_out = N.write_txt()
    con_out = N.write_i2b2_con()
    return txt_out, con_out




if __name__ == '__main__':
    main()
