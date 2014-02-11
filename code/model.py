from __future__ import with_statement

import time
import os
import pickle
import re
import subprocess
import sys
import nltk
import nltk.corpus.reader
import nltk.stem
import helper

from sets import Set
from sets import ImmutableSet

from wordshape import *

import libml
import features

class Model:
    sentence_features = ImmutableSet(["pos", "stem_wordnet", "test_result", "prev", "next"])
    word_features = ImmutableSet(["word", "length", "mitre", "stem_porter", "stem_lancaster", "word_shape"])
    # THESE ARE FEATURES I TRIED THAT DON'T LOOK THAT PROMISING
    # I have some faith in "metric_unit" and "has_problem_form"
    # "radial_loc" may be too rare and "def_class" could be over fitting
    # "metric_unit", "radial_loc", "has_problem_form", "def_class"

    labels = {
        "none": 0,
        "treatment": 1,
        "problem": 2,
        "test": 3
    }
    reverse_labels = {v: k for k, v in labels.items()}

    @staticmethod
    def load(filename='awesome.model'):
        with open(filename) as model:
            model = pickle.load(model)
        model.filename = filename
        return model

        # Constructor
    def __init__(self, filename='awesome.model', type=libml.ALL):
        model_directory = os.path.dirname(filename)

        if model_directory != "":
            helper.mkpath(model_directory)

        self.filename = os.path.realpath(filename)
        self.type = type
        self.vocab = {}

        self.enabled_features = Model.sentence_features | Model.word_features


        # Model::train()
        #
        # @param note. A Note object that has data for training the model
    def train(self, note):

        # Get the data and annotations from the Note object

        # data   - A list of list of the medical text's words
        # labels - A list of list of concepts (1:1 with data)
        data   = note.txtlist()
        labels = note.conlist()


                # rows is a list of a list of hash tables
        rows = []
        for sentence in data:
            rows.append(features.features_for_sentence(sentence))

                # each list of hash tables
        for row in rows:
                        # each hash table
            for feature_names in row:
                                # each key in hash table
                for feature in feature_names:
                                        # I think new word encountered
                    if feature not in self.vocab:
                        self.vocab[feature] = len(self.vocab) + 1

                # A list of a list encodings of concept labels (ex. 'none' => 0)
                # [ [0, 0, 0], [0], [0, 0, 0], [0], [0, 0, 0, 0, 0, 2, 2, 0, 1] ]
        label_lu = lambda l: Model.labels[l]
        labels = [map(label_lu, x) for x in labels]


                # list of a list of hash tables (all keys & values now numbers)
        feat_lu = lambda f: {self.vocab[item]: f[item] for item in f}
        rows = [map(feat_lu, x) for x in rows]


        libml.write_features(self.filename, rows, labels, self.type)

        with open(self.filename, "w") as model:
            pickle.dump(self, model)

                # Train the model
        libml.train(self.filename, self.type)



        # Model::predict()
        #
        # @param note. A Note object that contains the training data
    def predict(self, note):

        # data - A list of list of the medical text's words
        data = note.txtlist()

        # Something to do with calibrating the model
        rows = []   # rows <- list of a list of hash tables (feature vectors)
        for sentence in data:
            rows.append(features.features_for_sentence(sentence))


        feat_lu = lambda f: {self.vocab[item]: f[item] for item in f if item in self.vocab}
        rows = [map(feat_lu, x) for x in rows]
        libml.write_features(self.filename, rows, None, self.type)

            # Use the trained model to make predictions
        libml.predict(self.filename, self.type)


            # A hash table
        # the keys are 1,2,4 (SVM, LIN, and CRF)
        # each value is a list of concept labels encodings
        labels_list = libml.read_labels(self.filename, self.type)


            # translate labels_list into a readable format
            # ex. change all occurences of 0 -> 'none'
        for t, labels in labels_list.items():
            tmp = []
            for sentence in data:
                tmp.append([labels.pop(0) for i in range(len(sentence))])
                tmp[-1] = map(lambda l: l.strip(), tmp[-1])
                tmp[-1] = map(lambda l: Model.reverse_labels[int(l)], tmp[-1])
            labels_list[t] = tmp


            # The new labels_list is a translated version
        return labels_list