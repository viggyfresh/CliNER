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
import glob

import helper
import note



def main():

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
        dest = "out_file",
        help = "File to output data",
    )

    # Parse the command line arguments
    args = parser.parse_args()


    print 'CALLING FORMAT.PY'
    return


    # A list of text    file paths
    # A list of concept file paths
    txt_files = glob.glob(args.txt)
    con_files = glob.glob(args.con)
    xml_files = glob.glob(args.xml)

    # ex. {'record-13': 'record-13.txt'}
    # ex. {'record-13': 'record-13.con'}
    txt_files_map = helper.map_files(txt_files)
    con_files_map = helper.map_files(con_files)


    # ex. training_list =  [ ('record-13.txt', 'record-13.con') ]
    file_list = []
    for k in txt_files_map:
        if k in con_files_map:
            file_list.append((txt_files_map[k], con_files_map[k]))


    # i2b2 -> xml
    for txt_f,con_f in file_list:
        out = i2b2_to_xml(txt_f, con_f)
        #print out


    # xml -> i2b2
    for xml_f in xml_files:
        print xml_f
        txt_out, con_out = xml_to_i2b2(xml_f)
        print ''
        print txt_out
        print '\n--------\n'
        print con_out
        print ''



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


    # Read note from i2b2 format
    N = note.Note()
    N.read_xml(xml)

    # Output note into xml format
    txt_out = N.write_txt()
    con_out = N.write_i2b2_con()
    return txt_out, con_out




if __name__ == '__main__':
    main()
