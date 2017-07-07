from difflib import get_close_matches
import time
import re
import numpy

class BrownCluster(object):

    longest_n_gram = 4

    def __init__(self, path):
        """ takes in path to output of cluster implementation """

        self.process_path(path)

    def process_path(self, path):

        # TODO: put better preprocessing...
        output = open(path, "rb").read()
        output = [line.split('\t') for line in output.split('\n')]
        output.pop()

        d = {}

        for line in output:
            d[re.sub(r"[^A-Za-z0-9]", "", line[1].lower())] = {'cluster':line[0], 'count':line[2]}

        self.clusters = d
        self.vocab = set(self.clusters)

        self.groups = {}

        # get first n alphanumerics and group them.
        for n in range(1, BrownCluster.longest_n_gram):
            self.groups[n] = self.n_gram_group(self.vocab, n)


    def n_gram_group(self, vocab, gram_length):
        groups = {}

        for word in vocab:

            n_gram = self.get_first_n_alphanum(word, gram_length)

            if n_gram in groups:
                groups[n_gram].append(word)
            else:
                groups[n_gram] = [word]

        return groups


    def get_vocab_size(self):
        return len(self.clusters)


    def get_first_n_alphanum(self, string, gram_length):
        """ used for speeing up vocab matching """

        n_gram = re.search(r"[A-Za-z0-9]{}".format('{'+str(gram_length)+'}'), string)

        if n_gram is not None:
            n_gram = n_gram.group()

        return n_gram

    def get_match(self, string, gram_length=1):

        string = string.lower()
        ret_val = []

        for n in range(BrownCluster.longest_n_gram - 1, 0, -1):

            group = self.groups[n]

            n_gram = self.get_first_n_alphanum(string, n)

            if n_gram is not None or n == 1:

                for match in get_close_matches(string,
                                               group[n_gram],
                                               n=1,
                                               cutoff=.95):
                    ret_val.append(self.clusters[match])

            if len(ret_val) > 0:
                break

        return ret_val

    def get_first_n_bits(self, string, n):

        match = self.get_match(string)

        if match == []:
            return ""

        cluster_str = match[0]['cluster']

        if n < 0:
            return cluster_str

        return cluster_str[:n]

if __name__ == '__main__':

    bc = BrownCluster("/home/kwacome/unlabelled_data/corpus2-c100-p1.out/paths")

    init = time.time()

    print bc.get_first_n_bits('blood', -1)
    print bc.get_first_n_bits('blood', 0)
    print bc.get_first_n_bits('blood', 1 )
    print bc.get_first_n_bits('blood', 3)
    print bc.get_first_n_bits('blood', 1000)

    print time.time() - init


