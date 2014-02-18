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

import clicon_genia_interface


class FeatureWrapper:


    # Run the GENIA tagger on the given data
    def __init__(self, data):
        #self.GENIA_features = clicon_genia_interface.genia(data)
        self.GENIA_counter = 0



    # Iterate through GENIA Tagger features
    def next_GENIA_line(self):

        # End of list - reset counter & return None
        if self.GENIA_counter == len(self.GENIA_features):
            self.GENIA_counter = 0
            return None

        # Advance to next line
        self.GENIA_counter += 1

        return self.GENIA_features[self.GENIA_counter-1]




    # IOB_features()
    #
    # input:  A sentence
    # output: A hash table of features
    def IOB_features_for_sentence(self, sentence):

        isProse = self.prose_sentence(sentence)

        # Different features depending on whether sentence is 'prose'
        if isProse:
            line_features = self.IOB_prose_features_for_sentence(sentence)
        else:
            line_features = self.IOB_nonprose_features_for_sentence(sentence)

        # Return features as well as indication of whether it is prose or not
        return (isProse, line_features)



    # IOB_prose_features_for_sentence()
    #
    # input:  A sentence
    # output: A hash table of features
    def IOB_prose_features_for_sentence(self, sentence):


        # List of dictionaries of features
        line_features = [ {('dummy',1):1} for _ in sentence ]

        # Feature: Generic# stemmed word
        for i,word in enumerate(sentence):
            generic = re.sub('[0-9]','0',word)
            line_features[i].update( { ('Generic#',generic) : 1})

        # Feature: Previous word
        line_features[0].update(     { (        'prev_word',           '<START>' ) : 1} )
        for i in range(1,len(sentence)):
            line_features[i].update( { ('uncased_prev_word',sentence[i-1].lower()) : 1} )

        # Feature Uncased previous word
        line_features[0].update(     { ('uncased_prev_word',           '<START>' ) : 1} )
        for i in range(1,len(sentence)):
            line_features[i].update( { (        'prev_word',sentence[i-1]        ) : 1} )

        # Feature: Last two leters of word
        for word in sentence:
            line_features[i].update( { ('last_two_letters',word[-2:]) : 1} )

        # Feature: Previous POS
        pos_tagged = nltk.pos_tag(sentence)
        line_features[0].update( { ('prev_POS','<START>') : 1} )
        for i in range(1,len(sentence)):
            line_features[i].update( { ('prev_POS',pos_tagged[i-1]) : 1} )

        # Feature: 1-token part-of-speech context
        for (i,(_,pos)) in enumerate(pos_tagged):
            line_features[i].update( { ('pos',pos) : 1} )

        # Feature: UMLS concept hypernyms

        # GENIA features
        for i in range(len(sentence)):

            # FIXME - Do not call GENIA features right now
            #         (to speed up runtime during development)
            continue

            # Get the GENIA features of the current sentence
            genia_feats = self.next_GENIA_line()
            if not genia_feats: genia_feats = self.next_GENIA_line()


            # Feature: Current word's GENIA features
            keys = ['GENIA-stem','GENIA-POS','GENIA-chunktag']
            curr = genia_feats[i]
            output =  dict( (('curr-'+k, curr[k]), 1) for k in keys if k in curr)

            # Feature: Previous word's GENIA features
            if i:
                prev = genia_feats[i]
                output =  dict( (('prev-'+k,   prev[k]), 1) for k in keys if k in prev)
            else:
                output =  dict( (('prev-'+k, '<START>'), 1) for k in keys if k in curr)

            # Feature: Next word's GENIA stem
            # Note: This is done retroactively, updating the previous token
            if i > 0:
               line_features[i-1].update( {('next-GENIA-stem',curr['GENIA-stem']) : 1} )
            # Do not accidentally skip the final token
            if i == (len(sentence) - 1):
                line_features[i].update( { ('next-GENIA-stem','<END>') : 1} )

            line_features[i].update(output)

        # MetaMap semantic type


        return line_features



    # IOB_nonprose_features_for_sentence()
    #
    # input:  A sentence
    # output: A hash table of features
    def IOB_nonprose_features_for_sentence(self, sentence):

        # Get the GENIA features of the current sentence
        # The GENIA featurs are not used for nonprose, but it keeps things aligned for the prose
        #genia_feats = self.next_GENIA_line()
        #if not genia_feats: genia_feats = self.next_GENIA_line()

        # If sentence is empty
        if not sentence: return {}

        # List of dictionaries of features
        line_features = [ {('dummy',1):1} for _ in sentence ]

        # Feature: The word, itself
        for i,word in enumerate(sentence):
            line_features[i].update( { ('word',word.lower()) : 1} )

        # Feature: QANN uncased word

        # Feature: Uncased previous word
        line_features[0].update( { ('uncased_prev_word','<START>') : 1} )
        for i in range(1,len(sentence)):
            line_features[i].update( { ('uncased_prev_word',sentence[i-1].lower()) : 1} )

        # 3-token part-of-speech context

        # MetaMap semantic type

        # MetaMap CUI

        # Feature: Previous POS
        pos_tagged = nltk.pos_tag(sentence)
        line_features[0].update( { ('prev_POS','<START>') : 1} )
        for i in range(1,len(sentence)):
            line_features[i].update( { ('prev_POS',pos_tagged[i-1]) : 1} )

        return line_features



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


    # prose::word()
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
    #           3) A list of all indices into 1 that have been deemed nontrivial
    def generate_chunks(self, data, IOB_tags, labels=None):

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
                # concet_line in "012" instead of "IOB"
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




    # concept_features()
    #
    # input:  A sentence/line from a medical text file (list of chunks)
    #         An index into the sentence to indentify the given chunk
    # output: A list of hash tables (one hash table per word)
    def concept_features(self, sentence, ind):

        retVal = {}

        retVal.update( { ('chunk',sentence[ind]) :  1 } )

        # Feature: Uncased unigrams
        for i,word in enumerate( sentence[ind].split() ):
            featname = 'unigram-%d' % i
            retVal.update( { (featname, word.lower()) :  1 } )

        # Feature: First four letters of each word
        prefix_list = [ word[0:4] for word in sentence[ind].split() ]
        for i,word in enumerate(prefix_list):
            featname = 'first-four-letters-%d' % i
            retVal.update( { (featname, word) :  1 } )

        # Feature: Stemmed previous word


        # Feature: Uncased previous bigram


        # Feature: Argument type + nearest predicate


        # Feature: UMLS concept type


        # Feature Wikipedia concept type

        return retVal


