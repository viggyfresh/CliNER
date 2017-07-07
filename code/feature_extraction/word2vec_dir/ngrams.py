
import time
import numpy as np
from nltk import skipgrams
from nltk import ngrams

def map_rndm_vect(ngrams, D):

    # TODO: experiment with different distributions
    # TODO: assert that all vects are unique

    return {gram:np.random.randn(D) for gram in ngrams}

def get_char_grams(text, n):
    """ get character based ngrams

    concatenates a tokenized sentence
    turns in a list of chars
    get character ngrams usuing nltk

    @param text: a tokenized sentence of strings ex: ["an", "example"]
    """

    text = ' '.join(text)
    chars = [c for c in text]

    return set([''.join(t) for t in ngrams(chars, n)])


def get_char_skip_grams(text, n, k):

    text = ' '.join(text)
    chars = [c for c in text]

    return set([''.join(t) for t in skipgrams(chars, n, k)])


def get_char_gram_mappings(tokenized_sentences, D):

    ngrams = set()

    for s in tokenized_sentences:

        ngrams.update(get_char_grams(s, 1))

        for n in range(2,5):

            ngrams.update(get_char_skip_grams(s, n, 1))

    return map_rndm_vect(ngrams, D)


if __name__ == "__main__":

    init_time = time.time()

    print get_char_grams(["he", "ran"], 1)

    """
    skip_grams = get_char_skip_grams(["he", "ran", "to", "class", "and", "was", "late", "world!"], 2, 1)
    gram_mappings = map_rndm_vect(skip_grams, 200)

    token = "class"

    print get_lexical_vectors(token, gram_mappings)
    """

    print time.time() - init_time

