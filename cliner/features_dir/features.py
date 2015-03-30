######################################################################
#  CliCon - clicon_features.py                                       #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Isolate the model's features from model.py               #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Jan. 27, 2014'



import nltk
import re

from wordshape import getWordShapes
from utilities import is_prose_sentence

from sentence_features import SentenceFeatures



class FeatureWrapper:

    # FIXME - Make three objects - one for each classifier


    # Instantiate an FeatureWrapper object
    def __init__(self, data=None):

        # Sentence-level features
        self.feat_sent = SentenceFeatures(data)



    def extract_IOB_features(self, sentence):
        """
        extract_IOB_features()

        @param sentence. A list of chunks
        @return          tuple: boolean (Prose or not), a list of dictionaries of features

        """
        # Different features depending on whether sentence is 'prose'
        isProse = is_prose_sentence(sentence)

        if isProse:
            features_list = self.feat_sent.IOB_prose_features(sentence)
        else:
            features_list = self.feat_sent.IOB_nonprose_features(sentence)

        # Return features as well as indication of whether it is prose or not
        return (isProse, features_list)



    def concept_features(self, sentence, chunk_inds):
        """
        concept_features()

        @param sentence.   a list of chunks
        @param chunk_inds. a list of important indices of the sentence
        @return            a list of dictionaries of features

        """
        # FIXME - move all of this work to SentenceFeatures object

        '''
        # VERY basic feature set for sanity check tests during development
        features_list = []
        for i,ind in enumerate(chunk_inds):
            features = {('phrase',sentence[ind]) : 1} 
            features_list.append(features)
        return features_list
        '''

        # Create a list of feature sets (one per chunk)
        features_list = self.feat_sent.concept_features_for_sentence(sentence,chunk_inds)
        return features_list

