

import os
import sys
import glob
import cPickle as pickle
import cProfile as profile

from notes.note       import Note
from model            import Model




def main():

    if 'all' in sys.argv:
        txts = os.listdir(os.path.join(os.getenv('CLICON_DIR'),'data/train/txt'))
    elif 'big' in sys.argv:
        txts = glob.glob( os.path.join(os.getenv('CLICON_DIR'),'data/concept_assertion_relation_training_data/beth/txt/record-[2345]*.txt'))
        txts = [ os.path.split(t)[-1] for t in txts ]
    else:
        #txts = ['record-15.txt', 'record-13.txt']
        txts = ['record-15.txt']
        #txts = ['record-58.txt']


    notes = []
    for t in txts:

        if '.txt' not in t:
            continue

        base = t[:-4]
        print base

        # Read data
        note = Note('i2b2')
        txt = os.path.join(os.getenv('CLICON_DIR'),'data/train/txt/%s.txt'% base)
        con = os.path.join(os.getenv('CLICON_DIR'),'data/train/con/%s.con'% base)
        note.read(txt,con)

        # Add to list
        notes.append(note)


    # Get the data and annotations from the Note objects
    text    = [  note.getTokenizedSentences()  for  note  in  notes  ]
    ioblist = [  note.getIOBLabels()           for  note  in  notes  ]

    data1 = reduce( concat,    text )
    Y1    = reduce( concat, ioblist )


    # Train classifier (side effect - saved as object's member variable)
    m = Model()
    m.first_train(data1, Y1, do_grid=False)


    # Pickle dump
    print 'pickle dump'
    filename = os.path.join(os.getenv('CLINER_DIR'), 'models/dev-word2vec-first.model')
    with open(filename, "wb") as model:
        pickle.dump(m, model)




def concat(a,b):
    return a+b



if __name__ == '__main__':
    if 'profile' in sys.argv:
        profile.run('main()')
    else:
        main()
