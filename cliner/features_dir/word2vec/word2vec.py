#
#  read binary model of official word2vec vectors
#
#  https://groups.google.com/forum/#!searchin/word2vec-toolkit/python/word2vec-toolkit/GFNZkoDPd0g/7EJ2If34gjAJ
#


from os import path
from collections import defaultdict
import numpy as np



def load_bin(fname):
    """
    Loads 300x1 word vecs from Google (Mikolov) word2vec
    """
    word_vecs = {}
    print '\n\tloading word2vec embeddings'
    with open(fname, "rb") as f:
        header = f.readline()
        vocab_size, layer1_size = map(int, header.split())
        # dev speedup
        vocab_size = 20000
        binary_len = np.dtype('float32').itemsize * layer1_size
        i = 0
        for line in xrange(vocab_size):
            i += 1
            if (i%(vocab_size/20)) == 0:
                print '\t\t%5.1f%%' % (100*float(i)/vocab_size)
            word = []
            while True:
                ch = f.read(1)
                if ch == ' ':
                    word = ''.join(word)
                    break
                if ch != '\n':
                    word.append(ch)
            word_vecs[word] = np.fromstring(f.read(binary_len), dtype='float32')
    print '\tword2vec embeddings complete'
    return word_vecs


# Load word vectors
vectors_bin = path.join(path.dirname(path.abspath(__file__)), 'embeddings.bin')
pretrained = load_bin(vectors_bin)

# be able to handle OOV by giving them 0 vectors
embeddings = defaultdict(lambda:np.zeros(len(pretrained.values()[0])))
embeddings.update(pretrained)

