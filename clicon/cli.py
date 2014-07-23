import click
import os
import sys
import subprocess


@click.group()
def clicon():
    pass



# Train
@clicon.command()
@click.option('--annotations', 
              help='Concept files for training.')
@click.option('--model', 
              help='Model output by train.')
@click.option('--format', 
              help='Data format (i2b2 or xml).')
@click.argument('input')
def train(annotations, model, format, input):


    # Command line arguments
    if not annotations:
        print >>sys.stderr, '\n\tError: Must provide annotations for text files'
        print >>sys.stderr,  ''
        exit(1)


    # Base directory
    BASE_DIR = os.environ.get('CLICON_DIR')
    if not BASE_DIR:
        raise Exception('Environment variable CLICON_DIR must be defined')


    # Executable
    runable = os.path.join(BASE_DIR,'clicon/train.py')


    # Data paths
    txt_path   = os.path.join(BASE_DIR,       input)
    con_path   = os.path.join(BASE_DIR, annotations)


    # Build command
    cmd = ['python', runable, '-t', txt_path, '-c', con_path]


    # Optional arguments
    if model:
        model_path = os.path.join(BASE_DIR, model)
        cmd += ['-m', model_path]
    if format:
        cmd += ['-f',     format]


    # Execute train.py
    subprocess.call(cmd)



# Predict
@clicon.command()
@click.option('--model', 
              default='models/run_models/run.model',
              help='Model used to predict on files')
@click.option('--out', 
              default='data/test_predictions',
              help='The directory to write the output')
@click.option('--format', 
              default='i2b2',
              help='Data format (i2b2 or xml).')
@click.argument('input')
def predict(model, out, format, input):


    # Base directory
    BASE_DIR = os.environ.get('CLICON_DIR')
    if not BASE_DIR:
        raise Exception('Environment variable CLICON_DIR must be defined')


    # Executable
    runable = os.path.join(BASE_DIR,'clicon/predict.py')


    # Data paths
    txt_path   = os.path.join(BASE_DIR, input)


    # Build command
    cmd = ['python', runable, '-i', txt_path]


    # Optional arguments
    if out:
        out_path   = os.path.join(BASE_DIR,   out)
        cmd += ['-o',   out_path]
    if model:
        model_path = os.path.join(BASE_DIR, model)
        cmd += ['-m', model_path]
    if format:
        cmd += ['-f',     format]


    # Execute train.py
    subprocess.call(cmd)




if __name__ == '__main__':
    clicon()


