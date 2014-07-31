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

from sentence_features import SentenceFeatures



class FeatureWrapper:

    # FIXME - Make three objects - one for each classifier


    # Instantiate an FeatureWrapper object
    def __init__(self, data=None):

        # Sentence-level features
        self.feat_sent = SentenceFeatures(data)



    # IOB_features()
    #
    # input:  A sentence
    # output: A hash table of features
    def IOB_features(self, sentence):

        # Different features depending on whether sentence is 'prose'
        isProse = self.prose_sentence(sentence)

        if isProse:
            features_list = self.feat_sent.IOB_prose_features(sentence)
        else:
            features_list = self.feat_sent.IOB_nonprose_features(sentence)

        # Return features as well as indication of whether it is prose or not
        return (isProse, features_list)



    # concept_features()
    #
    # input:  A sentence/line from a medical text file (list of chunks)
    #         An list of indices into the sentence for each important chunk
    # output: A list of hash tables of features
    def concept_features(self, sentence, chunk_inds):
        
        # FIXME - move all of this work to SentenceFeatures object

        features_list = [ {} for _ in chunk_inds ]


        '''
        # VERY basic feature set for sanity check tests during development
        for i,ind in enumerate(chunk_inds):
            features = {('phrase',sentence[ind]) : 1} 
            features_list[i] = features
        return features_list
        '''


        tags = []

        for i,ind in enumerate(chunk_inds):

            # Create a list of feature sets (one per chunk)
            features = self.feat_sent.concept_features_for_chunk(sentence,ind)

            # Feature: Previous 3 POSs
            if 'prev_3_pos' in self.feat_sent.enabled_concept_features:
                tags = tags = nltk.pos_tag(sentence)
                if ind == 0:
                    prev_pos = ('*','*','*')
                    features[('prev_3_pos',prev_pos)] = 1
                elif ind == 1:
                    prev_pos = ('*','*',tags[0][1])
                    features[('prev_3_pos',prev_pos)] = 1
                elif ind == 2:
                    prev_pos = ('*',tags[0][1],tags[1][1])
                    features[('prev_3_pos',prev_pos)] = 1
                else:
                    prev_pos = (tags[ind-3][1],tags[ind-2][1],tags[ind-1][1])
                    features[('prev_3_pos',prev_pos)] = 1


            # Feature: Previous Chunks's Features
            if "prev" in self.feat_sent.enabled_concept_features:
                if ind == 0:
                    features[("prev", "*")] = 1
                else:
                    # Get features of previous chunks
                    prev_features = self.feat_sent.concept_features_for_chunk(sentence,ind-1)
                    prepend = lambda f: {("prev_"+k[0],k[1]):v for k, v in f.items()}
                    features.update( prepend(prev_features) ) 


            # Feature: Next Chunk's Features
            if "next" in self.feat_sent.enabled_concept_features:
                if ind == len(sentence) - 1:
                    features[("next", "*")] = 1
                else:
                    # Get features of previous chunks
                    next_features = self.feat_sent.concept_features_for_chunk(sentence,ind+1)
                    prepend = lambda f: {("next_"+k[0],k[1]):v for k, v in f.items()}
                    features.update( prepend(next_features) ) 

            features_list[i] = features


        return features_list



    # prose_sentence()
    #
    # input:  A sentence
    # output: Boolean yes/no
    def prose_sentence(self, sentence):

        # Empty sentence is not prose
        if not sentence:
            return False

        if sentence[-1] == '.' or sentence[-1] == '?':
            return True
        elif sentence[-1] == ':':
            return False
        elif len(sentence) <= 5:
            return False
        elif self.at_least_half_nonprose(sentence):
            return True
        else:
            return False


    # at_least_half_nonprose()
    #
    # input:  A sentence
    # output: A bollean yes/no
    def at_least_half_nonprose(self, sentence):

        count = 0

        for word in sentence:
            if self.prose_word(word):
                count += 1

        if count >= len(sentence):
            return True
        else:
            return False


    # prose_word()
    #
    # input:  A word
    # output: Boolean yes/no
    def prose_word(self, word):

        # Punctuation
        for punc in ".?,!:\"'":
            if re.search(punc, word):
                return False

        # Digit
        if re.match('\d', word):
            return False

        # All uppercase
        if word == word.upper():
            return False

        # Else
        return True




# generate_chunks()
#
# input: Three arguments:
#           1) A list of list of word (the data of the file)
#           2) A list of list of IOB tags (one-to-one with list from arg 1)
#           3) A list of list of concepts (one-to-one with list from arg 1)
#
#
# output: A 3-tuple of:
#           1) A list of list of chunks (word token phrases)
#           2) A list of list of concepts (one-to-one with list from ret 1)
#           3) A list of all indices into 1 of all non-'none' concepts
def generate_chunks(data, IOB_tags, labels=None):

    # List of list of tokens (similar to 'text', but concepts are grouped)
    text_chunks   = []

    # one-to-one concept classification with text_chunks
    if labels:
        concept_chunks = []
    else:
       concept_chunks = None

    # List of (line,token) pairs for classifications that are nont 'none'
    hits = []

    # Create tokens of full concept boundaries for second classifier
    for i, concept_line in enumerate(IOB_tags):

        # One line of 'chunked'
        line_of_text_chunks    = []
        if labels: line_of_concept_chunks = []

        # stores the current streak
        queue = []

        # Necessary when multiple concepts are on one line
        # The second concept's j index is relative to a word-split array
        # The j of the new token should be relative to how chunks there are
        chunk_offset = 0

        # C-style array indexing. Probably could be done a better way.
        # Used because I needed the ability of lookahead
        for j in range(len(concept_line)):

            # Outside
            # concept_line in "012" instead of "IOB"
            if concept_line[j] == 'O':
                line_of_text_chunks.append(data[i][j])
                if labels: line_of_concept_chunks.append('none')

            # Beginning of a concept boundary
            else:

                # Increase size of current streak
                queue.append(data[i][j])

                # lookahead (check if streak will continue)
                if (j+1 == len(concept_line))or \
                   (concept_line[j+1] != 'I'):     # end of classifiation

                       # Add full concept token
                       line_of_text_chunks.append(' '.join(queue))
                       if labels: line_of_concept_chunks.append(labels[i][j])

                       # Store indices of detected concept
                       hits.append( ( i, j + 1-len(queue) - chunk_offset ) )

                       # Reminder: used in the case that a concept follows a
                       #           multi-word concept on the same line
                       chunk_offset += len(queue) - 1

                       # Reset streak
                       queue = []

        text_chunks.append(line_of_text_chunks)
        if labels: concept_chunks.append(line_of_concept_chunks)


    return (text_chunks, concept_chunks, hits)

