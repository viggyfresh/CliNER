import click
import os
import commands


@click.group()
def clicon():
    pass



# Train
@clicon.command()
@click.option('--txt', 
              default='data/concept_assertion_relation_training_data/beth/txt/record-13.txt',
              help='Text files for training.')
@click.option('--con', 
              default='data/concept_assertion_relation_training_data/beth/concept/record-13.con',
              help='Concept files for training.')
@click.option('--model', 
              default='models/run_models/run.model',
              help='Model output by train.')
@click.option('--clicon_dir', 
              envvar='CLICON_DIR',
              help='Base CliCon directory (should be shell env variable).')
def train(txt, con, model, clicon_dir):

    # Base directory
    if not clicon_dir:
        raise Exception('Environment variable CLICON_DIR must be defined')
    BASE_DIR = clicon_dir

    # Executable
    runable = os.path.join(BASE_DIR,'clicon/train.py')

    # Command line arguments
    txt_path   = os.path.join(BASE_DIR,   txt)
    con_path   = os.path.join(BASE_DIR,   con)
    model_path = os.path.join(BASE_DIR, model)

    # Build command
    cmd = 'python ' + runable                         \
                    + ' -t \"'  + txt_path    + '\"'  \
                    + ' -c \"'  + con_path    + '\"'  \
                    + ' -m '    + model_path

    # Execute train.py
    #print '\tBASE_DIR: ', BASE_DIR
    #print '\tcmd: ', cmd
    #return
    errnum, output = commands.getstatusoutput(cmd)

    #print '\terrnum: ', errnum

    #print '\toutput:'
    for line in output.split('\n'):
        #print '\t\t', line
        print line



# Predict
@clicon.command()
@click.option('--txt', 
              default='data/concept_assertion_relation_training_data/beth/txt/record-13.txt',
              help='Text files for training.')
@click.option('--output',
              default='data/test_predictions',
              help='The directory to write the output')
@click.option('--model', 
              default='models/run_models/run.model',
              help='Model used to predict on files')
@click.option('--clicon_dir', 
              envvar='CLICON_DIR',
              help='Base CliCon directory (should be shell env variable).')
def predict(txt, output, model, clicon_dir):

    # Base directory
    if not clicon_dir:
        raise Exception('Environment variable CLICON_DIR must be defined')
    BASE_DIR = clicon_dir

    # Executable
    runable = os.path.join(BASE_DIR,'clicon/predict.py')

    # Command line arguments
    txt_path    = os.path.join(BASE_DIR,    txt)
    output_path = os.path.join(BASE_DIR, output)
    model_path  = os.path.join(BASE_DIR,  model)

    # Build command
    cmd = 'python ' + runable                         \
                    + ' -i \"'  + txt_path    + '\"'  \
                    + ' -o '    + output_path         \
                    + ' -m '    + model_path

    # Execute train.py
    #print '\tBASE_DIR: ', BASE_DIR
    #print '\tcmd: ', cmd
    errnum, output = commands.getstatusoutput(cmd)

    #print '\terrnum: ', errnum

    #print '\toutput:'
    for line in output.split('\n'):
        #print '\t\t', line
        print line



if __name__ == '__main__':
    clicon()


