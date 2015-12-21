

import os
import sys
import glob
from collections import defaultdict

from notes.note       import Note
from model            import Model

from features_dir import utilities




def main():

    if 'all' in sys.argv:
        txts = glob.glob( os.path.join(os.getenv('CLICON_DIR'),'data/test_data/*.txt') )
        txts = [ os.path.split(f)[-1]  for f in txts ]
    elif 'big' in sys.argv:
        txts = glob.glob( os.path.join(os.getenv('CLICON_DIR'),'data/test_data/00[2345]*.txt') )
        txts = [ os.path.split(f)[-1]  for f in txts ]
    else:
        txts = ['record-15.txt']
        #txts = ['record-65.txt']
        #txts = ['0033.txt']
        #txts = ['record-58.txt']
        #txts = ['0106.txt']


    txts = sorted(txts)

    # Confusion matrix
    labels_map = {'B':0, 'I':1, 'O':2}
    lmap = sorted(labels_map.items())
    labels = [ k for k,v in lmap ]

    p_confusion = [[0] * len(labels) for e in labels]
    n_confusion = [[0] * len(labels) for e in labels]

    pincorrect = defaultdict(lambda:[])
    nincorrect = defaultdict(lambda:[])


    for t in txts:

        if '.txt' not in t: continue

        #try:
        for i in range(1):

            base = t[:-4]
            print base

            # Read data
            note = Note('i2b2')

            if 'record' in base:
                txt = os.path.join(os.getenv('CLICON_DIR'),'data/concept_assertion_relation_training_data/beth/txt/%s.txt' % base)
                con = os.path.join(os.getenv('CLICON_DIR'),'data/concept_assertion_relation_training_data/beth/concept/%s.con' % base)
            elif base[0] == '0':
                txt = os.path.join(os.getenv('CLICON_DIR'),'data/test_data/%s.txt' % base)
                con = os.path.join(os.getenv('CLICON_DIR'),'data/reference_standard_for_test_data/concepts/%s.con' % base)
            else:
                print 'Cound not locate concept file: ', base
                continue

            note.read(txt,con)


            # Get the data and annotations from the Note objects
            data   = note.getTokenizedSentences()


            # Predict IOB labels
            model= os.path.join(os.getenv('CLINER_DIR'),'models/dev-word2vec-first.model')
            m = Model.load(model)
            iobs, piobs, niobs = m.first_predict(data)


            # Parition prose and nonprose into two different lists
            gold = note.getIOBLabels()
            pdata   = []
            ndata   = []
            plabels = []
            nlabels = []
            for line,labs in zip(data,gold):
                if utilities.is_prose_sentence(line):
                    plabels.append(labs)
                    pdata.append(line)
                else:
                    nlabels.append(labs)
                    ndata.append(line)


            # FIXME - Do same for nonprose
            # Detect where prediction errors occured
            for i in range(len(pdata)):
                error = False
                for j in range(len(pdata[i])):
                    if piobs[i][j] != plabels[i][j]:
                        begin = j-2 if j-2>0 else 0
                        phrase =   pdata[i][begin:j+3]
                        pred   =   piobs[i][begin:j+3]
                        ref    = plabels[i][begin:j+3]
                        pincorrect[base].append( (phrase, pred, ref) )



            # Translate labels
            label_lu = lambda l: labels_map[l]
            p_predictions = [ map(label_lu, x) for x in piobs ]
            n_predictions = [ map(label_lu, x) for x in niobs ]

            p_reference   = [ map(label_lu, x) for x in plabels ]
            n_reference   = [ map(label_lu, x) for x in nlabels ]


            # Confusion matrix for prose
            for c, r in zip( p_predictions, p_reference ):
                for c, r in zip(c, r):
                    p_confusion[r][c] += 1

            # Confusion matrix for prose
            for c, r in zip( n_predictions, n_reference ):
                for c, r in zip(c, r):
                    n_confusion[r][c] += 1


        #except Exception, e:
        #    print '\nsomething went wrong: ', t
        #    print 'error: ', e
        #    print ''


    print 'PROSE'
    for fname,val in pincorrect.items():
        print 'fname:  ', fname
        for phrase,pred,ref in val:
            print 'sent:   ', list(enumerate(phrase))
            print 'labels: ', list( zip(range(len(phrase)), pred, ref) )
            print
        print '\n\n'



    # Results
    confusions  = [p_confusion, n_confusion]
    label_types = ['prose', 'nonprose']

    for confusion,label_type in zip(confusions,label_types):

        print ""
        print ""
        print ""
        print "================"
        print label_type + " Confusion Matrix"
        print "================"
        print ""
        pad = max(len(l) for l in labels) + 6
        print "%s %s" % (' ' * pad, "\t".join(labels))
        for act, act_v in lmap:
            print "%s %s" % (act.rjust(pad), "\t".join([str(confusion[act_v][pre_v]) for pre, pre_v in lmap]))
        print ""


        # Compute the analysis stuff
        precision = []
        recall = []
        specificity = []
        f1 = []

        tp = 0
        fp = 0
        fn = 0
        tn = 0

        print "Analysis"
        pad = 3
        print " " * pad, "Precision\tRecall\tSpceificity\tF1"


        for lab, lab_v in lmap:
            tp = confusion[lab_v][lab_v]
            fp = sum(confusion[v][lab_v] for k, v in lmap if v != lab_v)
            fn = sum(confusion[lab_v][v] for k, v in lmap if v != lab_v)
            tn = sum(confusion[v1][v2] for k1, v1 in lmap for k2, v2 in lmap if v1 != lab_v and v2 != lab_v)
            precision += [float(tp) / (tp + fp + 1e-100)]
            recall += [float(tp) / (tp + fn + 1e-100)]
            specificity += [float(tn) / (tn + fp + 1e-100)]
            f1 += [float(2 * tp) / (2 * tp + fp + fn + 1e-100)]
            print "%s %.4f\t%.4f\t%.4f\t\t%.4f" % (lab.rjust(pad), precision[-1], recall[-1], specificity[-1], f1[-1])

        print "--------"

        precision = sum(precision) / len(precision)
        recall = sum(recall) / len(recall)
        specificity = sum(specificity) / len(specificity)
        f1 = sum(f1) / len(f1)

        print "Average: %.4f\t%.4f\t%.4f\t%.4f" % (precision, recall, specificity, f1)




if __name__ == '__main__':
    main()
