#
#  read binary model of official word2vec vectors
#
#  https://groups.google.com/forum/#!searchin/word2vec-toolkit/python/word2vec-toolkit/GFNZkoDPd0g/7EJ2If34gjAJ
#


from os import path
from collections import defaultdict
import numpy as np

embeddings = None


def load_bin(fname, bin_mode=False):

    word_vecs = {}
    print '\n\tloading word2vec embeddings'

    if bin_mode is True:
        with open(fname, "rb") as f:
            header = f.readline()

            vocab_size, layer1_size = map(int, header.split())

            print "\n\tvocab size: {}".format(vocab_size)

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

#                print word
                word_vecs[word] = np.fromstring(f.read(binary_len), dtype='float32')

    else:

        # formatting per line, minus the header, is word <1st value> <2nd value> .... < nth value> where n is size of vector

        with open(fname, "rb") as f:

            header = f.readline()

            vocab_size, vector_size  = map(int, header.split())

            print "\n\t vocab size {}".format(vocab_size)
            print "\t vectorize size".format(vector_size)

            for i, line in enumerate(f):

                if (i%(vocab_size/20)) == 0:
                    print '\t\t%5.1f%%' % (100*float(i)/vocab_size)

                line = line.split(' ')

                word = line[0]
                vector = map(float, line[1:-1])

                assert len(vector) == vector_size

                word_vecs[word] = vector

    print '\tword2vec embeddings complete'
    return word_vecs



if embeddings is None:

    # Load word vectors
    vectors_bin = path.join(path.dirname(path.abspath(__file__)), 'mimic3_vect.bin')

    pretrained = load_bin(vectors_bin, bin_mode=True)

    # be able to handle OOV by giving them 0 vectors
    embeddings = defaultdict(lambda:np.zeros(len(pretrained.values()[0])))
    embeddings = defaultdict(lambda:np.array([.0000000000000000000000000001]*len(pretrained.values()[0])))
    embeddings.update(pretrained)

    #embeddings = pretrained

def cosine_similarity(x, y):
    return (np.inner(x,y) / (np.linalg.norm(x) * np.linalg.norm(y)))

def get_word_from_vec(vector):

    global embeddings

    # TODO: hacky
    if len(vector) != 300:
        exit("wrong dimensionality, should be 300")

    map(lambda word: similarity_measures.update({word: cosine_similarity(vector, embeddings[word])}), embeddings)

    return max(embeddings.keys(), key=lambda k:similarity_measures[k])


def compute_similarity_score(vector):

    global embeddings

    # TODO: hacky
    if len(vector) != 300:
        exit("wrong dimensionality, should be 300")

    similarity_measures = {}

    map(lambda word: similarity_measures.update({word: cosine_similarity(vector, embeddings[word])}), embeddings)

    sorted_candidates = sorted(zip(similarity_measures.keys(), similarity_measures.values()), key=lambda x: x[1])

    sorted_candidates.reverse()

    return sorted_candidates

def get_candidates(vector):

    candidates = compute_similarity_score(vector)

    return candidates[0:10]

print "blood" in embeddings


