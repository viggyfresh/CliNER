

import os
import sys
import glob
import cPickle as pickle
import cProfile as profile
import glob
import argparse

import helper

from notes.note       import Note
from model            import Model

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

    parser.add_argument("-m",
        dest = "model",
        help = "Path to the model that should be generated",
    )

    parser.add_argument("-f",
        dest = "format",
        help = "Data format ( " + ' | '.join(Note.supportedFormats()) + " )",
    )

    parser.add_argument("-g",
        dest = "grid",
        help = "A flag indicating whether to perform a grid search",
        action = "store_true"
    )

    parser.add_argument("-no-crf",
        dest = "nocrf",
        help = "A flag indicating whether to use crfsuite for pass one.",
        action = "store_true"
    )

    # Parse the command line arguments
    args = parser.parse_args()
    is_crf = not args.nocrf

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


    # A list of text    file paths
    # A list of concept file paths
    txt_files = glob.glob(args.txt)
    con_files = glob.glob(args.con)


    # data format
    if args.format:
        format = args.format
    else:
        print '\n\tERROR: must provide "format" argument\n'
        exit()


    # Must specify output format
    if format not in Note.supportedFormats():
        print >>sys.stderr, '\n\tError: Must specify output format'
        print >>sys.stderr,   '\tAvailable formats: ', ' | '.join(Note.supportedFormats())
        print >>sys.stderr, ''
        exit(1)


    # Collect training data file paths
    txt_files_map = helper.map_files(txt_files) # ex. {'record-13': 'record-13.con'}
    con_files_map = helper.map_files(con_files)

    training_list = []                          # ex. training_list =  [ ('record-13.txt', 'record-13.con') ]
    for k in txt_files_map:
        if k in con_files_map:
            training_list.append((txt_files_map[k], con_files_map[k]))


    # Read the data into a Note object
    notes = []
    for txt, con in training_list:
        try:
            note_tmp = Note(format)   # Create Note
            note_tmp.read(txt, con)   # Read data into Note
            notes.append(note_tmp)    # Add the Note to the list
        except NoteException, e:
            exit( '\n\tWARNING: Note Exception - %s\n\n' % str(e) )


    # Get the data and annotations from the Note objects
    text    = [  note.getTokenizedSentences()  for  note  in  notes  ]
    ioblist = [  note.getIOBLabels()           for  note  in  notes  ]

    data1 = reduce( concat,    text )
    Y1    = reduce( concat, ioblist )

    # file names
    if not notes:
        print 'Error: Cannot train on 0 files. Terminating train.'
        return 1

    # Create a Machine Learning model
    m = Model(is_crf=is_crf)

    m.first_train(data1, Y1, do_grid=False)

    # Pickle dump
    print 'pickle dump'
    filename = os.path.join(os.getenv('CLINER_DIR'), args.model)
    with open(filename, "wb") as model:
        pickle.dump(m, model)


def concat(a,b):
    return a+b



if __name__ == '__main__':
    if 'profile' in sys.argv:
        profile.run('main()')
    else:
        main()
