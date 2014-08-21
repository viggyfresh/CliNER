import os
import sys
import glob
import argparse
import helper

import sci
from model import Model
from note import *

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-i", 
        dest = "input", 
        help = "The input files to predict", 
        default = os.path.join(os.getenv('CLICON_DIR'), 'data/test_data/*')
    )

    parser.add_argument("-o", 
        dest = "output", 
        help = "The directory to write the output", 
        default = os.path.join(os.getenv('CLICON_DIR'), 'data/test_predictions')
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The model to use for prediction",
        default = os.path.join(os.getenv('CLICON_DIR'), 'models/run.model')
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

    args = parser.parse_args()


    # Parse arguments
    files = glob.glob(args.input)
    helper.mkpath(args.output)
    format = args.format


    # Must specify output format
    if (format != 'i2b2') and (format != 'xml'):
        print >>sys.stderr, '\n\tError: Must specify output format (i2b2 or xml)'
        print >>sys.stderr, ''
        exit(1)


    # Output directory
    helper.mkpath(os.path.join(args.output))


    # Load model
    model = Model.load(args.model)


    # Tell user if not predicting
    if not files:
        print >>sys.stderr, "\n\tNote: You did not supply any input files\n"
        exit()


    # For each file, predict concept labels
    for txt in files:

        # Read the data into a Note object
        note = Note()
        note.read_i2b2(txt)


        print '-' * 30
        print '\n\n\t', txt, '\n'


        # Predict concept labels
        labels = model.predict(note)


        # Get predictions in proper format
        if format == 'i2b2':
            extension = 'con'
            output = note.write_i2b2(labels)
        else:
            extension = 'xml'
            output = note.write_xml(labels)


        # Output file
        basename = os.path.basename(txt)[:-3] + extension
        out_path = os.path.join(args.output, basename)


        # Output the concept predictions
        print '\n\nwriting to: ', out_path
        with open(out_path, 'w') as f:
            print >>f, output
        print




if __name__ == '__main__':
    main()
