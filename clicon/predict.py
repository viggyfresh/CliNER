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
        default = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/test_data/*')
    )

    parser.add_argument("-o", 
        dest = "output", 
        help = "The directory to write the output", 
        default = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/test_predictions')
    )

    parser.add_argument("-m",
        dest = "model",
        help = "The model to use for prediction",
        default = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../models/run_models/run.model')
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


<<<<<<< HEAD
    # Is crfsuite installed?
    if args.with_crf:
        crfsuite = args.with_crf
    elif False:
        'DETECT CRFSUITE FROM CONFIG FILE'
        crfsuite = None
    else:
        crfsuite = None
=======
    # Must specify output format
    if (format != 'i2b2') and (format != 'xml'):
        print >>sys.stderr, '\n\tError: Must specify output format (i2b2 or xml)'
        print >>sys.stderr, ''
        exit(1)


    # Output directory
    helper.mkpath(os.path.join(args.output))
>>>>>>> documentation


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


<<<<<<< HEAD
        # Output directory
        con = os.path.split(txt)[-1]
        con = con[:-3] + 'con'


        helper.mkpath(os.path.join(args.output, "lin"))
        con_path = os.path.join(args.output, "lin", con)
=======
        # Get predictions in proper format
        if format == 'i2b2':
            extension = 'con'
            output = note.write_i2b2(labels)
        else:
            extension = 'xml'
            output =  note.write_xml(labels)

>>>>>>> documentation

        # Output file
        basename = os.path.basename(txt)[:-3] + extension
        out_path = os.path.join(args.output, basename)

<<<<<<< HEAD
        # Get predictions in proper format
        if format == 'i2b2':
            output = note.write_i2b2_con(labels)
        elif format == 'xml':
            output =  note.write_xml(labels)
        else:
            output = ''

        # Output the concept predictions
        print '\n\nwriting to: ', con_path
        with open(con_path, 'w') as f:
=======

        # Output the concept predictions
        print '\n\nwriting to: ', out_path
        with open(out_path, 'w') as f:
>>>>>>> documentation
            print >>f, output


        print ''



if __name__ == '__main__':
    main()
