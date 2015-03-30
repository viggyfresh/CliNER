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

        >>> fw = FeatureWrapper()
        >>> fw.extract_IOB_features(['this', 'is', 'a' 'test'])
        (False, [{('word_shape', 'LOWERif wordShaper =='): 1, ('next_word_shape', 'xx'): 1, ('mitre', 'CAPSMIX'): 1, ('next_umls_cui', u'C1193984'): 1, ('next_word', 'is'): 1, ('next_word_shape', 'LOWERif wordShaper =='): 1, ('next_umls_semantic_type_word', u'Intellectual Product'): 1, ('word_shape', 'ALL-LOWER'): 1, ('problem_form', None): 1, ('next_next_unigrams-1', 'atest'): 1, ('umls_cui', u'C1080058'): 1, ('next_umls_cui', u'C0441913'): 1, ('next_mitre', 'ALPHANUM'): 1, ('word', 'this'): 1, ('prog_location', None): 1, ('next_word_shape', 'WT-x:2'): 1, ('prev', '*'): 1, ('next_word_shape', 'ALL-LOWER'): 1, ('next_unigrams-1', 'atest'): 1, ('mitre', 'ALPHANUM'): 1, ('next_unigrams-1', 'is'): 1, ('next_prog_location', None): 1, ('next_problem_form', None): 1, ('word_shape', 'WT-x'): 1, ('umls_semantic_type_word', u'Eukaryote'): 1, ('next_prev_unigrams-0', 'this'): 1, ('word_shape', 'xxxx'): 1, ('next_mitre', 'CAPSMIX'): 1, ('next_umls_semantic_type_word', u'Plant'): 1}, {('prev_umls_semantic_type_word', u'Eukaryote'): 1, ('word_shape', 'LOWERif wordShaper =='): 1, ('next_word_shape', 'WT-x'): 1, ('prev_word_shape', 'WT-x'): 1, ('mitre', 'CAPSMIX'): 1, ('prev_word_shape', 'xxxx'): 1, ('prev_mitre', 'ALPHANUM'): 1, ('next_word', 'atest'): 1, ('word', 'is'): 1, ('umls_cui', u'C0441913'): 1, ('next_word_shape', 'ALL-LOWER'): 1, ('prev_mitre', 'CAPSMIX'): 1, ('prev_word_shape', 'LOWERif wordShaper =='): 1, ('prev_problem_form', None): 1, ('word_shape', 'ALL-LOWER'): 1, ('prev_umls_cui', u'C1080058'): 1, ('problem_form', None): 1, ('prev_next_unigrams-1', 'is'): 1, ('next_prev_unigrams-1', 'is'): 1, ('prev_next_unigrams-1', 'atest'): 1, ('next_word_shape', 'xxxxx'): 1, ('word_shape', 'WT-x:2'): 1, ('prev_word', 'this'): 1, ('next_mitre', 'ALPHANUM'): 1, ('prog_location', None): 1, ('umls_cui', u'C1193984'): 1, ('prev_prog_location', None): 1, ('next_word_shape', 'LOWERif wordShaper =='): 1, ('next_unigrams-1', 'atest'): 1, ('umls_semantic_type_word', u'Intellectual Product'): 1, ('mitre', 'ALPHANUM'): 1, ('next_prog_location', None): 1, ('word_shape', 'xx'): 1, ('prev_unigrams-0', 'this'): 1, ('prev_word_shape', 'ALL-LOWER'): 1, ('umls_semantic_type_word', u'Plant'): 1, ('next_prev_unigrams-0', 'this'): 1, ('next_mitre', 'CAPSMIX'): 1}, {('word_shape', 'LOWERif wordShaper =='): 1, ('mitre', 'CAPSMIX'): 1, ('prev_umls_cui', u'C0441913'): 1, ('prev_prev_unigrams-0', 'this'): 1, ('prev_mitre', 'CAPSMIX'): 1, ('word', 'atest'): 1, ('prev_word_shape', 'LOWERif wordShaper =='): 1, ('prev_problem_form', None): 1, ('word_shape', 'ALL-LOWER'): 1, ('prev_unigrams-1', 'is'): 1, ('prev_word_shape', 'xx'): 1, ('prev_next_unigrams-1', 'atest'): 1, ('next', '*'): 1, ('prog_location', None): 1, ('prev_word_shape', 'WT-x:2'): 1, ('prev_umls_semantic_type_word', u'Plant'): 1, ('prev_prog_location', None): 1, ('prev_mitre', 'ALPHANUM'): 1, ('word_shape', 'xxxxx'): 1, ('prev_word', 'is'): 1, ('mitre', 'ALPHANUM'): 1, ('prev_umls_cui', u'C1193984'): 1, ('prev_unigrams-0', 'this'): 1, ('prev_word_shape', 'ALL-LOWER'): 1, ('prev_umls_semantic_type_word', u'Intellectual Product'): 1, ('word_shape', 'WT-x'): 1}])
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

        >>> fw = FeatureWrapper()
        >>> fw.concept_features(['this', 'is', 'a', 'test'], [3])
        [{('umls_semantic_type_sentence', u'B'): 1, ('metric_unit', None): 1, ('umls_semantic_type_sentence', u'P'): 1, ('umls_semantic_context', u'Finding'): 1, ('umls_semantic_context', u'Quantitative Concept'): 1, ('umls_semantic_type_sentence', u'E'): 1, ('umls_semantic_context', u'Intellectual Product'): 1, ('umls_semantic_type_word', u'Intellectual Product'): 1, ('umls_semantic_context', u'Plant'): 1, 'dummy': 1, ('umls_cui', u'C0392366'): 1, ('umls_semantic_type_sentence', u'C'): 1, ('umls_semantic_context', u'Body Space or Junction'): 1, ('umls_semantic_context', u'Classification'): 1, ('umls_semantic_context', u'Eukaryote'): 1, ('umls_semantic_type_sentence', u'Q'): 1, ('umls_semantic_context', u'Temporal Concept'): 1, ('umls_semantic_context', u'Body Part, Organ, or Organ Component'): 1, ('umls_semantic_type_sentence', u'F'): 1, ('umls_semantic_type_sentence', u'I'): 1, ('umls_semantic_type_word', u'Finding'): 1, ('word', 'test'): 1, ('umls_cui', u'C0456984'): 1, ('umls_semantic_type_sentence', u'T'): 1}]
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

