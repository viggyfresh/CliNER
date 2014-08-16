import os
import os.path
import glob
import argparse
import helper
import libml

from sets import Set
from model import Model
from note import *


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", 
        dest = "txt", 
        help = "The files that contain the training examples",
        default = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/concept_assertion_relation_training_data/merged/txt/*')
    )
    
    parser.add_argument("-c", 
        dest = "con", 
        help = "The files that contain the labels for the training examples",
        default = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/concept_assertion_relation_training_data/merged/concept/*')
    )

    parser.add_argument("-m",
        dest = "model",
        help = "Path to the model that should be generated",
        default = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../models/run_models/run.model')
    )

    parser.add_argument("-d",
        dest = "disabled_features",
        help = "The features that should not be used",
        nargs = "+",
        default = None
    )

    parser.add_argument("-e",
        dest = "enabled_features",
        help = "The features that should be used. This option trumps -d",
        nargs = "+",
        default = None
    )

    parser.add_argument("-f",
        dest = "format",
        help = "Data format (i2b2 or xml).",
        default = 'i2b2'
    )

    parser.add_argument("-crf",
        dest = "with_crf",
        help = "Specify where to find crfsuite",
        default = None
    )


    # Parse the command line arguments
    args = parser.parse_args()


    # A list of text    file paths
    # A list of concept file paths
    txt_files = glob.glob(args.txt)
    con_files = glob.glob(args.con)


    # Is crfsuite installed?
    if args.with_crf:
        crfsuite = args.with_crf
    elif False:
        'DETECT CRFSUITE FROM CONFIG FILE'
        crfsuite = None
    else:
        crfsuite = None

    # i2b2 or xml
    format = args.format
    if format == 'i2b2':

        # ex. {'record-13': 'record-13.con'}
        txt_files_map = helper.map_files(txt_files)
        con_files_map = helper.map_files(con_files)

        # ex. training_list =  [ ('record-13.txt', 'record-13.con') ]
        training_list = []
        for k in txt_files_map:
            if k in con_files_map:
                training_list.append((txt_files_map[k], con_files_map[k]))

        # file names
        print '\n', training_list, '\n'

        # Read the data into a Note object
        notes = []
        for txt, con in training_list:
            note_tmp = Note()             # Create Note
            note_tmp.read_i2b2(txt, con)  # Read data into Note
            notes.append(note_tmp)        # Add the Note to the list


    elif format == 'xml':

        # file names
        print '\n', txt_files, '\n'

        # Read the data into a Note object
        notes = []
        for xml in txt_files:
            note_tmp = Note()             # Create Note
            note_tmp.read_xml(xml)        # Read data into Note
            notes.append(note_tmp)        # Add the Note to the list



    # file names
    if not notes:
        print 'Error: Cannot train on 0 files. Terminating train.'
        return 1


    # Create a Machine Learning model
    model = Model(filename = args.model)


    # Train the model using the Note's data
    model.train(notes)



if __name__ == '__main__':
    main()
