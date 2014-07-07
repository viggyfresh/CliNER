import click
import os
import commands


@click.group()
def clicon():
    pass



# Train
@clicon.command()
@click.option('--annotations', 
              default='data/concept_assertion_relation_training_data/beth/concept/record-13.con',
              help='Concept files for training.')
@click.option('--model', 
              default='models/run_models/run.model',
              help='Model output by train.')
@click.option('--format', 
              default='i2b2',
              help='Data format (i2b2 or xml).')
@click.argument('input')
def train(annotations, model, format, input):

    # Base directory
    BASE_DIR = os.environ.get('CLICON_DIR')
    if not BASE_DIR:
        raise Exception('Environment variable CLICON_DIR must be defined')

    # Executable
    runable = os.path.join(BASE_DIR,'clicon/train.py')

    # Command line arguments
    txt_path   = os.path.join(BASE_DIR,       input)
    con_path   = os.path.join(BASE_DIR, annotations)
    model_path = os.path.join(BASE_DIR,       model)

    print 'training'

    # Build command
    cmd = 'python ' + runable                         \
                    + ' -f   '  + format              \
                    + ' -t \"'  + txt_path    + '\"'  \
                    + ' -c \"'  + con_path    + '\"'  \
                    + ' -m '    + model_path

    # Execute train.py
    errnum, output = commands.getstatusoutput(cmd)

    # Display output
    for line in output.split('\n'):
        print line



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

    print 'BASE_DIR: ', BASE_DIR

    # Executable
    runable = os.path.join(BASE_DIR,'clicon/predict.py')

    # Command line arguments
    txt_path   = os.path.join(BASE_DIR, input)
    out_path   = os.path.join(BASE_DIR,   out)
    model_path = os.path.join(BASE_DIR, model)

    print 'predicting'

    # Build command
    cmd = 'python ' + runable                         \
                    + ' -f   '  + format              \
                    + ' -i \"'  + txt_path    + '\"'  \
                    + ' -o '    + out_path            \
                    + ' -m '    + model_path

    # Execute predict.py
    errnum, output = commands.getstatusoutput(cmd)

    # Display output
    for line in output.split('\n'):
        print line



if __name__ == '__main__':
    clicon()


