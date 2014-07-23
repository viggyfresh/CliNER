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

    args = parser.parse_args()


    # Parse arguments
    files = glob.glob(args.input)
    helper.mkpath(args.output)
    format = args.format


    # Load model
    model = Model.load(args.model)


    # For each file, predict concept labels
    for txt in files:

        # Read the data into a Note object
        note = Note()
        note.read_i2b2(txt)


        print '-' * 30
        print '\n\n\tfile: ', txt, '\n'


        # Predict concept labels
        labels = model.predict(note)


        # Output directory
        con = os.path.split(txt)[-1]
        con = con[:-3] + 'con'


        for t in sci.bits(model.type):

            if t == sci.LIN:
                helper.mkpath(os.path.join(args.output, "lin"))
                con_path = os.path.join(args.output, "lin", con)


            # Get predictions in proper format
            if format == 'i2b2':
                output = note.write_i2b2(labels[t])
            elif format == 'xml':
                output =  note.write_xml(labels[t])
            else:
                output = ''

            # Output the concept predictions
            with open(con_path, 'w') as f:
                print >>f, output


        print ''



if __name__ == '__main__':
    main()
