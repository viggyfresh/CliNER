import click
import os
import sys
import subprocess
import glob


@click.group()
def clicon():
    pass



# Train
@clicon.command()
@click.option('--annotations', help='Concept files for training.')
@click.option('--model'      , help='Model output by train.'     )
@click.option('--format'     , help='Data format (i2b2 or xml).' )
@click.option('--crfsuite'   , help='Path to crfsuite.'          )
@click.argument('input')
def train(annotations, model, format, crfsuite, input):


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


    # Build command
    cmd = ['python', runable, '-t', input, '-c', annotations]


    # Optional arguments
    if model:
        cmd += ['-m'  ,    model]
    if format:
        cmd += ['-f'  ,   format]
    if crfsuite:
        cmd += ['-crf', crfsuite]


    # Execute train.py
    subprocess.call(cmd)




# Predict
@clicon.command()
@click.option('--out'   , help='The directory to write the output')
@click.option('--model' , help='Model used to predict on files'   )
@click.option('--format', help='Data format (i2b2 or xml).'       )
@click.option('--crfsuite'   , help='Path to crfsuite.'          )
@click.argument('input')
def predict(model, out, format, crfsuite, input):


    # Base directory
    BASE_DIR = os.environ.get('CLICON_DIR')
    if not BASE_DIR:
        raise Exception('Environment variable CLICON_DIR must be defined')


    # Executable
    runable = os.path.join(BASE_DIR,'clicon/predict.py')


    # Build command
    cmd = ['python', runable, '-i', input]


    # Optional arguments
    if out:
        cmd += ['-o',    out]
    if model:
        cmd += ['-m',  model]
    if format:
        cmd += ['-f', format]
    if crfsuite:
        cmd += ['-crf', crfsuite]


    # Execute train.py
    subprocess.call(cmd)





# Format
@clicon.command()
@click.option('--annotations', help='Concept files for training.'      )
@click.option('--format'     , help='Data format (i2b2 or xml).'       )
@click.option('--out'        , help='The directory to write the output')
@click.argument('input')
def format(annotations, format, out, input):


    # Base directory
    BASE_DIR = os.environ.get('CLICON_DIR')
    if not BASE_DIR:
        raise Exception('Environment variable CLICON_DIR must be defined')


    # Executable
    runable = os.path.join(BASE_DIR,'clicon/format.py')


    # Must have legal input
    files = glob.glob(input)
    if not files:
        print >>sys.stderr, '\n\tError: Input file could not be found\n'
        exit(1)

    # Must manually check if '.txt' or 'xml'
    if   files[0][-3:] == 'xml':
        flag = '-x'
    elif files[0][-3:] == 'txt':
        flag = '-t'
    else:
        print >>sys.stderr, '\n\tError: Input file must be either "txt" or "xml"'
        print >>sys.stderr, ''
        exit(2)


    # Build command
    cmd = ['python', runable, flag, input]


    # Optional arguments
    if annotations:
        cmd += ['-c', annotations]
    if out:
        cmd += ['-o',         out]
    if format:
        cmd += ['-f',      format]


    # Execute train.py
    subprocess.call(cmd)








if __name__ == '__main__':
    clicon()


