######################################################################
#  CliCon - clicon_features.py                                       #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Isolate the model's features from model.py               #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Jan. 27, 2014'


from wordshape import getWordShapes
from utilities import is_prose_sentence

import sentence_features as feat_sent

def IOB_prose_features(data, Y=None):
    """
    IOB_prose_features()

    @param data      A list of split sentences (1 sent = 1 line from file)
    @param Y         A list of list of IOB (1:1 mapping with data)
    @return          tuple: list of IOB_prose_features, list of IOB 

    """
    
    prose   = []
    pchunks = []

    # If no Y given, that information doesn't matter
    if not Y:
        Y = data

    for sentence,labels in zip(data, Y):
        if is_prose_sentence(sentence):
           prose.append(feat_sent.IOB_prose_features(sentence, data))
           pchunks += labels

    return (prose, pchunks)


def IOB_nonprose_features(data, Y=None):
    """
    IOB_nonprose_features()

    @param data      A list of split sentences (1 sent = 1 line from file)
    @param Y         A list of list of IOB (1:1 mapping with data)
    @return          tuple: list of IOB_prose_features, list of IOB 

    """
    
    nonprose   = []
    nchunks    = []
    
    # If no Y given, that information doesn't matter
    if not Y:
        Y = data

    for sentence,labels in zip(data, Y):
        if not is_prose_sentence(sentence):
           nonprose.append(feat_sent.IOB_nonprose_features(sentence))
           nchunks += labels

    return (nonprose, nchunks)


def concept_features(sentence, chunk_inds):
    """
    concept_features()

    @param sentence.   a list of chunks
    @param chunk_inds. a list of important indices of the sentence
    @return            a list of dictionaries of features

    >>> concept_features(['this', 'is', 'an', 'important', 'test'], [3, 4]) is not None
    True
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
    features_list = feat_sent.concept_features_for_sentence(sentence,chunk_inds)
    return features_list

