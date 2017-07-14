######################################################################
#  CliNER - train.py                                                 #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Build model for given training data.                     #
######################################################################


import os
import os.path
import glob
import argparse
import cPickle as pickle
import sys

import helper
from sets import Set
from model import ClinerModel
from notes.documents import Document

# base directory
CLINER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--txt",
        dest = "txt",
        help = "The files that contain the training examples",
    )
    parser.add_argument("--annotations",
        dest = "con",
        help = "The files that contain the labels for the training examples",
    )
    parser.add_argument("--model",
        dest = "model",
        help = "Path to the model that should be generated",
    )
    parser.add_argument("--log",
        dest = "log",
        help = "Path to the log file for training info",
        default = os.path.join(CLINER_DIR, 'models', 'train.log')
    )
    parser.add_argument("--use-lstm",
        dest = "use_lstm",
        help = "Whether to use an LSTM model",
        action = 'store_true',
        default = False
    )
    parser.add_argument("--format",
        dest = "format",
        help = "Data format ( i2b2 )"
    )


    # Parse the command line arguments
    args = parser.parse_args()

    # Error check: Ensure that file paths are specified
    if not args.txt:
        print >>sys.stderr, '\n\tError: Must provide text files'
        print >>sys.stderr,  ''
        exit(1)
    if not args.con:
        print >>sys.stderr, '\n\tError: Must provide annotations for text files'
        print >>sys.stderr,  ''
        exit(1)
    if not args.model:
        print >>sys.stderr, '\n\tError: Must provide valid path to store model'
        print >>sys.stderr,  ''
        exit(1)
    modeldir = os.path.dirname(args.model)
    if (not os.path.exists(modeldir)) and (modeldir != ''):
        print >>sys.stderr, '\n\tError: Model dir does not exist: %s' % modeldir
        print >>sys.stderr,  ''
        exit(1)

    # A list of txt and concept file paths
    txt_files = glob.glob(args.txt)
    con_files = glob.glob(args.con)


    # data format
    if args.format:
        format = args.format

    # Must specify output format
    if args.format not in ['i2b2']:
        print >>sys.stderr, '\n\tError: Must specify output format'
        print >>sys.stderr,   '\tAvailable formats: i2b2'
        print >>sys.stderr, ''
        exit(1)


    # Collect training data file paths
    txt_files_map = helper.map_files(txt_files) 
    con_files_map = helper.map_files(con_files)
    
    training_list = []

    for k in txt_files_map:
        if k in con_files_map:
            training_list.append((txt_files_map[k], con_files_map[k]))

    # Train the model
    train(training_list, args.model, args.format, args.use_lstm, logfile=args.log)




def train(training_list, model_path, format, use_lstm,  logfile=None):

    # Read the data into a Document object
    docs = []
    for txt, con in training_list:
        doc_tmp = Document(txt,con)
        docs.append(doc_tmp)


    # file names
    if not docs:
        print 'Error: Cannot train on 0 files. Terminating train.'
        return 1

    # Create a Machine Learning model
    model = ClinerModel(use_lstm)

    # Train the model using the Documents's data
    model.train(docs)

    # Pickle dump
    print '\nserializing model to %s\n' % model_path
    with open(model_path, "wb") as m_file:
        pickle.dump(model, m_file)
    #model.log(logfile   , model_file=model_path)
    #model.log(sys.stdout, model_file=model_path)
    

if __name__ == '__main__':
    main()
