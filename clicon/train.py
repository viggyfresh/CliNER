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
    #default = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../models/awesome.model')
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

    parser.add_argument("--no-svm",
        dest = "no_svm",
        action = "store_true",
        help = "Disable SVM model generation",
    )

    parser.add_argument("--no-lin",
        dest = "no_lin",
        action = "store_true",
        help = "Disable LIN model generation",
    )

    parser.add_argument("--no-crf",
        dest = "no_crf",
        action = "store_true",
        help = "Disable CRF model generation",
    )


    # Parse the command line arguments
    args = parser.parse_args()


    # A list of text    file paths
    # A list of concept file paths
    txt_files = glob.glob(args.txt)
    con_files = glob.glob(args.con)

    txt_files_map = helper.map_files(txt_files)
    con_files_map = helper.map_files(con_files)


    # ex. training_list =  [ ('record-13.txt', 'record-13.con') ]
    training_list = []
    for k in txt_files_map:
        if k in con_files_map:
            training_list.append((txt_files_map[k], con_files_map[k]))


    # What kind of model should be used? (ex. SVM vs. CRF)
    type = 0
    if not args.no_svm:
        type = type | libml.SVM
    if not args.no_lin:
        type = type | libml.LIN
    if not args.no_crf:
        type = type | libml.CRF


    # file names
    print training_list
    if not training_list:
        print 'Error: Cannot train on 0 files. Terminating train.'
        return 1


    # Read the data into a Note object
    notes = []
    for txt, con in training_list:
        note_tmp = Note()                # Create Note
        note_tmp.read_i2b2(txt, con)     # Read data into Note
        notes.append(note_tmp)           # Add the Note to the list


    # Create a Machine Learning model
    model = Model(filename = args.model, type = type)

    if args.disabled_features != None:
        model.enabled_features = model.enabled_features - Set(args.disabled_features)
    if args.enabled_features != None:
        model.enabled_features = Set(args.enabled_features)


    # Train the model using the Note's data
    model.train(notes)


if __name__ == '__main__':
    main()
