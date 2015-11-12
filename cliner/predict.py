######################################################################
#  CliNER - predict.py                                               #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Use trained model to predict concept labels for data.    #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Oct. 5, 2014'


import os
import sys
import glob
import argparse
import helper

from model import Model
from notes.note import Note


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-i",
        dest = "input",
        help = "The input files to predict",
    )

    parser.add_argument("-o",
        dest = "output",
        help = "The directory to write the output",
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The model to use for prediction",
    )

    parser.add_argument("-f",
        dest = "format",
        help = "Data format ( " + ' | '.join(Note.supportedFormats()) + " )",
    )

    parser.add_argument("-crf",
        dest = "with_crf",
        help = "Specify where to find crfsuite",
        default = None
    )

    args = parser.parse_args()

    # Error check: Ensure that file paths are specified
    if not args.input:
        print >>sys.stderr, '\n\tError: Must provide text files\n'
        exit(1)
    if not args.output:
        print >>sys.stderr, '\n\tError: Must provide output directory\n'
        exit(1)
    if not args.model:
        print >>sys.stderr, '\n\tError: Must provide path to model\n'
        exit(1)
    if not os.path.exists(args.model):
        print >>sys.stderr, '\n\tError: Model does not exist: %s\n' % args.model
        exit(1)


    # Parse arguments
    files = glob.glob(args.input)
    helper.mkpath(args.output)

    if args.format:
        format = args.format
    else:
        print '\n\tERROR: must provide "format" argument\n'
        exit()


    # Predict
    predict(files, args.model, args.output, format=format)



def predict(files, model_path, output_dir, format):

    # Must specify output format
    if format not in Note.supportedFormats():
        print >>sys.stderr, '\n\tError: Must specify output format'
        print >>sys.stderr,   '\tAvailable formats: ', ' | '.join(Note.supportedFormats())
        print >>sys.stderr, ''
        exit(1)


    # Load model
    model = Model.load(model_path)


    # Tell user if not predicting
    if not files:
        print >>sys.stderr, "\n\tNote: You did not supply any input files\n"
        exit()


    # For each file, predict concept labels
    n = len(files)
    for i,txt in enumerate(sorted(files)):

        note = Note(format)

        # Output file
        extension = note.getExtension()
        fname = os.path.splitext(os.path.basename(txt))[0] + '.' + extension
        out_path = os.path.join(output_dir, fname)
        '''
        if os.path.exists(out_path):
            #print '\tWARNING: prediction file already exists (%s)' % out_path
            continue
        '''

        # Read the data into a Note object
        note.read(txt)


        print '-' * 30
        print '\n\t%d of %d' % (i+1,n)
        print '\t', txt, '\n'


        # Predict concept labels
        labels = model.predict(note)

        # Get predictions in proper format
        output = note.write(labels)


        # Output the concept predictions
        print '\n\nwriting to: ', out_path
        with open(out_path, 'w') as f:
            print >>f, output
        print



if __name__ == '__main__':
    main()
