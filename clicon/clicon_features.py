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
from sets import ImmutableSet
from wordshape import getWordShapes

import clicon_genia_interface

from umls_cache import UmlsCache
import umls



class FeatureWrapper:


    # Feature Enabling
    enabled_IOB_prose_sentence_features = ImmutableSet( [ 'umls_semantic_type_sentence', 'pos', 'stem_wordnet', 'umls_semantic_context', 'GENIA', 'prev', 'next', 'prev_3_pos'] )
    enabled_IOB_prose_word_features     = ImmutableSet( ['Generic#', 'last_two_letters', 'word', 'mitre', 'stem_porter', 'word_shape', 'metric_unit','umls_cui' 'umls_hypernyms' ] )

    enabled_IOB_nonprose_sentence_features = ImmutableSet( ['prev_pos', 'pos', 'next_pos', 'test_result', 'umls_semantic_context', 'prev', 'next','prev_3_pos'])
    enabled_IOB_nonprose_word_features     = ImmutableSet( ['word', 'uncased_prev_word','umls_semantic_type_word', 'word_shape', 'metric_unit', 'mitre', 'directive', 'umls_cui', 'umls_hypernyms'] )

    enabled_concept_features = ImmutableSet( [ 'umls_semantic_type_sentence' , 'umls_semantic_type_word','pos','stem_wordnet', 'test_result', 'word', 'length', 'mitre', 'stem_porter', 'stem_lancaster', 'word_shape','prev','next', 'umls_semantic_context', 'prev_3_pos', 'umls_cui'])


    # Instantiate an FeatureWrapper object
    def __init__(self, data=None):

        # Only run GENIA tagger if feature is enabled
        if (data) and ('GENIA' in self.enabled_IOB_prose_sentence_features):
            self.GENIA_features = clicon_genia_interface.genia(data)
            self.GENIA_counter = 0

        # cache for the mappings of all umls lookups made
        self.umls_lookup_cache = UmlsCache()



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

        #return (True,self.IOB_prose_features_for_sentence(sentence))

        isProse = self.prose_sentence(sentence)

        # Different features depending on whether sentence is 'prose'
        if isProse:
            features_list =    self.IOB_prose_features_for_sentence(sentence)
        else:
            features_list = self.IOB_nonprose_features_for_sentence(sentence)

        # Return features as well as indication of whether it is prose or not
        return (isProse, features_list)



    # IOB_prose_features_for_sentence()
    #
    # input:  A sentence
    # output: A list of hash tables of features
    def IOB_prose_features_for_sentence(self, sentence):

        features_list = []
        flag = 0 

        # Get a feature set for each word in the sentence
        for i,word in enumerate(sentence):
            features_list.append( self.IOB_prose_features_for_word(sentence,i) )


        # Only POS tag once
        pos_tagged = []

        # Used for 'prev' and 'next' features
        ngram_features = [{} for i in range(len(features_list))]


        # Allow for particular features to be enabled
        for feature in self.enabled_IOB_prose_sentence_features:

            # Feature: Part of Speech
            if feature == 'pos':
                pos_tagged = pos_tagged or nltk.pos_tag(sentence)
                for (i,(_,pos)) in enumerate(pos_tagged):
                    features_list[i].update( { ('pos',pos) : 1} )

            # Feature: UMLS semantic type for the sentence
            if feature == 'umls_semantic_type_sentence':

                # a list of the uml semantic of the largest substring(s).
                sentence_mapping = umls.umls_semantic_type_sentence( self.umls_lookup_cache,  sentence )

                # If there are no mappings.
                if( len(sentence_mapping) == 0 ):
                    for i , features in enumerate( features_list):
                        features[(feature , None ) ] = 1
                # assign the umls definitions to the vector for each word
                else:
                    for i , features in enumerate( features_list):
                        for concepts in sentence_mapping:
                            if concepts:
                                 for concept in concepts:
                                     features[(feature,concept[0])] = 1
                            else:
                                features[(feature , None ) ] = 1

            # Feature: UMLS semantic concext
            if feature == 'umls_semantic_context':

                # umls definition of the largest string the word is in
                umls_semantic_context_mappings = umls.umls_semantic_context_of_words( self.umls_lookup_cache , sentence )

                #print umls_semantic_context_mappings 

                # assign umls definitions to the each chunk
                for i , features in enumerate( features_list ):

                    #if there are no mappings
                    if umls_semantic_context_mappings[i] == None:
                        features[(feature,None)] = 1
                    # there could be multiple contexts
                    else:
                        for mapping in umls_semantic_context_mappings[i]:
                            for concept in mapping:
                                features[(feature,concept[0])] = 1

            # Feature: Previous 3 POSs
            if feature == 'prev_3_pos':
                pos_tagged = pos_tagged or nltk.pos_tag(sentence)
                for i in range(len(sentence)):
                    if i == 0:
                        prev_pos = ('*','*','*')
                        features_list[0].update({(feature,prev_pos)       :1})
                    elif i == 1:
                        prev_pos = ('*','*',pos_tagged[0][1])
                        features_list[1].update({(feature,prev_pos)       :1})
                    elif i == 2:
                        prev_pos = ('*',pos_tagged[0][1],pos_tagged[1][1])
                        features_list[2].update({(feature,prev_pos)       :1})
                    else:
                        prev_pos = (pos_tagged[i-3][1],pos_tagged[i-2][1],pos_tagged[i-1][1])
                        features_list[i].update({(feature,pos_tagged[i-1]):1})
            

            # GENIA features
            if feature == 'GENIA':

                # Get the GENIA features of the current sentence
                genia_feats = self.next_GENIA_line()
                if not genia_feats: genia_feats = self.next_GENIA_line()

                #print genia_feats

                for i in range(len(sentence)):

                    #print i

                    # Feature: Current word's GENIA features
                    keys = ['GENIA-stem','GENIA-POS','GENIA-chunktag']
                    curr = genia_feats[i]
                    output =  dict( (('curr-'+k, curr[k]), 1) for k in keys if k in curr)

                    # Feature: Previous word's GENIA features
                    if i == 0:
                        output =  dict( (('prev-'+k, '<START>'), 1) for k in keys if k in curr)
                    else:
                        prev = genia_feats[i]
                        output =  dict( (('prev-'+k,   prev[k]), 1) for k in keys if k in prev)

                    # Feature: Next word's GENIA stem
                    # Note: This is done by updating the previous token's dict
                    if i != (len(sentence) - 1):
                       features_list[i-1].update( {('next-GENIA-stem',curr['GENIA-stem']) : 1} )
                    else:
                        features_list[i].update( { ('next-GENIA-stem','<END>') : 1} )

                    features_list[i].update(output)
                
        ngram_features = [{} for i in range(len(features_list))]
        if "prev" in self.enabled_IOB_prose_sentence_features:
            prev = lambda f: {("prev_"+k[0], k[1]): v for k,v in f.items()}
            prev_list = map(prev, features_list)
            for i in range(len(features_list)):
                if i == 0:
                    ngram_features[i][("prev", "*")] = 1
                else:
                    ngram_features[i].update(prev_list[i-1])

        if "next" in self.enabled_IOB_prose_sentence_features:
            next = lambda f: {("next_"+k[0], k[1]): v for k,v in f.items()}
            next_list = map(next, features_list)
            for i in range(len(features_list)):
                if i == len(features_list) - 1:
                    ngram_features[i][("next", "*")] = 1
                else:
                    ngram_features[i].update(next_list[i+1])

        merged = lambda d1, d2: dict(d1.items() + d2.items())
        features_list = [merged(features_list[i], ngram_features[i]) 
            for i in range(len(features_list))]

        return features_list



    # IOB_prose_features_for_word()
    #
    # input:  A single word
    # output: A dictionary of features
    def IOB_prose_features_for_word(self, sentence, i):

        # Abbreviation for most features,
        #    although some will require index for context
        word = sentence[i]


        # Feature: <dummy>
        features = {'dummy': 1}  # always have >0 dimensions


        # Allow for particular features to be enabled
        for feature in self.enabled_IOB_prose_word_features:


            # Feature: Generic# stemmed word
            if feature == 'Generic#':
                generic = re.sub('[0-9]','0',word)
                features.update( { ('Generic#',generic) : 1 } )


            # Feature: Last two leters of word
            if feature == 'last_two_letters':
                features.update( { ('last_two_letters',word[-2:]) : 1 } )


            # Feature: Previous word
            if feature == 'prev_word':
                if i == 0:
                    features.update( {('prev_word',    '<START>' ) : 1} )
                else:
                    features.update( {('prev_word', sentence[i-1]) : 1} )

            # Feature: UMLS Semantic Types
            if feature == 'umls_cui':

                # Get UMLS CUIs (could have multiple)
                cuis = umls.get_cui(self.umls_lookup_cache , word)

                # Add each CUI
                if cuis:
                    for cui in cuis:
                        features[(feature,cui)] = 1
                else:
                    features[(feature,None)] = 1
                
            # Feature: UMLS Hypernyms
            if feature == 'umls_hypernyms':
            
                # Get UMLS hypernyms
                hyps = umls.umls_hypernyms(self.umls_lookup_cache,word)

                # Add all hypernyms
                if hyps:
                    #for hyp in hyps:
                    features[(feature,hyps[0])] = 1
                else:
                    features[(feature,None)] = 1


            # FIXME - adding pass two features to pass 1 (good? bad?)
            if feature == "word":
                features[(feature, word)] = 1

            if feature == "length":
                features[(feature, None)] = len(word)

            if feature == "mitre":
                for f in self.mitre_features:
                    if re.search(self.mitre_features[f], word):
                        features[(feature, f)] = 1

            if feature == "stem_porter":
                st = nltk.stem.PorterStemmer()
                features[(feature, st.stem(word))] = 1

            if feature == "stem_lancaster":
                st = nltk.stem.LancasterStemmer()
                features[(feature, st.stem(word))] = 1

            if feature == "word_shape":
                wordShapes = getWordShapes(word)
                for j, shape in enumerate(wordShapes):
                    features[(feature + str(j), shape)] = 1


        return features




    # IOB_nonprose_features_for_sentence()
    #
    # input:  A sentence
    # output: A hash table of features
    def IOB_nonprose_features_for_sentence(self, sentence):

        # Get the GENIA features of the current sentence
        #    (not used for nonprose, but it keeps things aligned for the prose)
        if 'GENIA' in self.enabled_IOB_prose_sentence_features:
            genia_feats = self.next_GENIA_line()
            if not genia_feats: genia_feats = self.next_GENIA_line()

        # If sentence is empty
        #if not sentence: return {}

        features_list = []

        # Get a feature set for each word in the sentence
        for i,word in enumerate(sentence):
            features_list.append( self.IOB_nonprose_features_for_word(sentence,i) )

        # Only POS tag once
        pos_tagged = []

        # Allow for particular features to be enabled
        for feature in self.enabled_IOB_nonprose_sentence_features:

            # Feature: Previous POS
            if feature == 'prev_pos':
                pos_tagged = pos_tagged or nltk.pos_tag(sentence)
                for i in range(len(sentence)):
                    if i == 0:
                        features_list[0].update({('prev_POS','<START>')      :1})
                    else:
                        features_list[i].update({('prev_POS',pos_tagged[i-1]):1})

            # Feature: Part of Speech
            if feature == 'pos':
                pos_tagged = pos_tagged or nltk.pos_tag(sentence)
                for (i,(_,pos)) in enumerate(pos_tagged):
                    features_list[i].update( { ('pos',pos) : 1} )

            # Feature: Previous POS
            if feature == 'next_pos':
                pos_tagged = pos_tagged or nltk.pos_tag(sentence)
                for i in range(len(sentence)):
                    if i == len(sentence)-1:
                        features_list[-1].update({('prev_POS','<START>')     :1})
                    else:
                        features_list[i].update({('prev_POS',pos_tagged[i-1]):1})

            # Feature: Test Result (for each chunk)
            if feature == "test_result":
                for index, features in enumerate(features_list):
                    right = " ".join([w for w in sentence[index:]])
                    if self.is_test_result(right):
                        features[(feature, None)] = 1

            # Feature: UMLS semantic context
            if feature == 'umls_semantic_context':
                # the umls definition of the largest string the word is in
                umls_semantic_context_mappings = umls.umls_semantic_context_of_words( self.umls_lookup_cache , sentence )

                # Semantic contxt of each word
                for i in range(len(sentence)):

                    #if there are no mappings
                    if umls_semantic_context_mappings[i] == None:
                        features_list[i][(feature,None)] = 1
                    # there could be multiple contexts
                    else:
                        for mapping in umls_semantic_context_mappings[i]:
                            for concept in mapping:
                                features_list[i][(feature,concept[0])] = 1

            # Feature: Previous 3 POSs
            if feature == 'prev_3_pos':
                pos_tagged = pos_tagged or nltk.pos_tag(sentence)
                for i in range(len(sentence)):
                    if i == 0:
                        prev_pos = ('*','*','*')
                        features_list[0].update({(feature,prev_pos)       :1})
                    elif i == 1:
                        prev_pos = ('*','*',pos_tagged[0][1])
                        features_list[1].update({(feature,prev_pos)       :1})
                    elif i == 2:
                        prev_pos = ('*',pos_tagged[0][1],pos_tagged[1][1])
                        features_list[2].update({(feature,prev_pos)       :1})
                    else:
                        prev_pos = (pos_tagged[i-3][1],pos_tagged[i-2][1],pos_tagged[i-1][1])
                        features_list[i].update({(feature,pos_tagged[i-1]):1})
            


        ngram_features = [{} for i in range(len(features_list))]
        if "prev" in self.enabled_IOB_nonprose_sentence_features:
            prev = lambda f: {("prev_"+k[0], k[1]): v for k,v in f.items()}
            prev_list = map(prev, features_list)
            for i in range(len(features_list)):
                if i == 0:
                    ngram_features[i][("prev", "*")] = 1
                else:
                    ngram_features[i].update(prev_list[i-1])

        if "next" in self.enabled_IOB_nonprose_sentence_features:
            next = lambda f: {("next_"+k[0], k[1]): v for k,v in f.items()}
            next_list = map(next, features_list)
            for i in range(len(features_list)):
                if i == len(features_list) - 1:
                    ngram_features[i][("next", "*")] = 1
                else:
                    ngram_features[i].update(next_list[i+1])

        merged = lambda d1, d2: dict(d1.items() + d2.items())
        features_list = [merged(features_list[i], ngram_features[i]) 
            for i in range(len(features_list))]

        return features_list



    # IOB_nonprose_features_for_word()
    #
    # input:  A single word
    # output: A dictionary of features
    def IOB_nonprose_features_for_word(self, sentence, i):

        # Abbreviation for most features,
        #    although some will require index for context
        word = sentence[i]


        # Feature: <dummy>
        features = {'dummy': 1}  # always have >0 dimensions


        # Allow for particular features to be enabled
        for feature in self.enabled_IOB_nonprose_word_features:

            # Feature: The word, itself
            if feature == 'word':
                features.update( { ('word',word.lower()) : 1} )

            # Feature: Uncased previous word
            if feature == 'uncased_prev_word':
                if i == 0:
                    features.update( {('uncased_prev_word','<START>'            ) : 1} )
                else:
                    features.update( {('uncased_prev_word',sentence[i-1].lower()) : 1} )

            # Feature: UMLS Semantic Type
            if feature == 'umls_semantic_type_word':
                # Get a semantic type for each unigram
                mapping = umls.umls_semantic_type_word(self.umls_lookup_cache,word )

                #If there is at least one umls semantic type.
                if mapping:
                    for concept in mapping:
                        features[('umls_semantic_type_word' , concept )] = 1
                else:
                    features[('umls_semantic_type_word' ,   None  )] = 1

            # Feature: UMLS Semantic Types
            if feature == 'umls_cui':
                # Get UMLS CUIs (could have multiple)
                cuis = umls.get_cui(self.umls_lookup_cache , word)

                # Add each CUI
                if cuis:
                    for cui in cuis:
                        features[(feature,cui)] = 1
                else:
                    features[(feature,None)] = 1

            # Feature: UMLS Hypernyms
            if feature == 'umls_hypernyms':
            
                # Get UMLS hypernyms
                hyps = umls.umls_hypernyms(self.umls_lookup_cache,word)

                # Add all hypernyms
                if hyps:
                    #for hyp in hyps:
                    features[(feature,hyps[0])] = 1
                else:
                    features[(feature,None)] = 1


            # Feature: Metric Unit
            if feature == "metric_unit":
                tests = 3
                unit = 0
                if self.is_weight(word):
                    unit = 1 / tests
                elif self.is_size(word):
                    unit = 2 / tests
                elif self.is_volume(word):
                    unit = 3 / tests
                features[(feature, None)] = unit

            # Feature: Date
            if feature == 'date':
                if self.is_date(word):
                    features[(feature,None)] = 1
                else:
                    features[(feature,None)] = 0

            # Feature: Directive
            if feature == 'directive':
                if self.is_directive(word):
                    features[(feature,None)] = 1
                else:
                    features[(feature,None)] = 0

            # Feature: Mitre
            if feature == "mitre":
                for f in self.mitre_features:
                    if re.search(self.mitre_features[f], word):
                        features[(feature, f)] = 1

            # Feature: Word Shape
            if feature == "word_shape":
                wordShapes = getWordShapes(word)
                for j, shape in enumerate(wordShapes):
                    features[('word_shape', shape)] = 1

        return features




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



    # concept_features()
    #
    # input:  A sentence/line from a medical text file (list of chunks)
    #         An index into the sentence to indentify the given chunk
    # output: A hash table of features
    def concept_features(self, sentence, ind):

        # Create a list of feature sets (one per chunk)
        features = self.concept_features_for_chunk(sentence,ind)

        tags = []

        # Feature: Previous 3 POSs
        if 'prev_3_pos' in self.enabled_concept_features:
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

        # Feature: UMLS semantic type for the sentence
        if 'umls_semantic_type_sentence' in self.enabled_concept_features:
            # a list of the uml semantic of the largest substring(s).
            sentence_mapping = umls.umls_semantic_type_sentence( self.umls_lookup_cache,  sentence )

            #print sentence_mapping

             # if there are no mappings
            if not sentence_mapping:
                features[('umls_semantic_type_sentence', None ) ] = 1
            # assign the umls definitions to the vector for each word
            else:
                
                for concept in sentence_mapping:
                    if concept:
                        for mapping in concept:
                            features[('umls_semantic_type_sentence' , mapping[0] ) ] = 1
                    else:
                        features[('umls_semantic_type_sentence' ,   None  ) ] = 1
#            print features 
        # Feature: Previous Chunks's Features
        if "prev" in self.enabled_concept_features:
            if ind == 0:
                features[("prev", "*")] = 1
            else:
                # Get features of previous chunks
                prev_features = self.concept_features_for_chunk(sentence,ind-1)
                prepend = lambda f: {("prev_"+k[0], k[1]): v for k, v in f.items()}
                features.update( prepend(prev_features) ) 


        # Feature: Next Chunk's Features
        if "next" in self.enabled_concept_features:
            if ind == len(sentence) - 1:
                features[("next", "*")] = 1
            else:
                # Get features of previous chunks
                next_features = self.concept_features_for_chunk(sentence,ind+1)
                prepend = lambda f: {("next_"+k[0], k[1]): v for k, v in f.items()}
                features.update( prepend(next_features) ) 

        return features



    # concept_features_for_chunk()
    #
    # input:  A sentence/line from a medical text file (list of chunks)
    #         An index into the sentence to indentify the given chunk
    # output: A hash table of features
    def concept_features_for_chunk(self, sentence, ind):

        features = {}

        # Feature: <dummy>
        features = {'dummy': 1}  # always have >0 dimensions

        # Split the chunked sentence into a list of words for (POS tagger)
        split_sentence = []
        split_ind = 0
        for chun in sentence:
            for word in chun.split():
                split_sentence.append(word)
            split_ind += len(chun.split())

        tags = None


        # Allow for particular features to be enabled
        for feature in self.enabled_concept_features:

            # Feature: Word (each word)
            if feature == "word":
                for i,word in enumerate(sentence[ind].split()):
                    featname = 'word-%d' % i
                    features.update( { (featname,word) : 1} )

            # Feature: Length (of each word)
            if feature == "length":
                for i,word in enumerate(sentence[ind].split()):
                    featname = 'length-%d' % i
                    features.update( { (featname,None) : len(word)} )

            # Feature: Mitre (of each word)
            if feature == "mitre":
                for i,word in enumerate(sentence[ind].split()):
                    for f in self.mitre_features:
                        if re.search(self.mitre_features[f], word):
                            featname = 'mitre'
                            features.update( { (featname,f) : 1} )

            # Feature: Porter Stem (of each word)
            if feature == "stem_porter":
                for i,word in enumerate(sentence[ind].split()):
                    featname = 'stem_porter-%d' % i
                    st = nltk.stem.PorterStemmer()
                    features[(featname, st.stem(word))] = 1

            # Feature: Lancaster Stem (of each word)
            if feature == "stem_lancaster":
                for i,word in enumerate(sentence[ind].split()):
                    featname = 'stem_lancaster-%d' % i
                    st = nltk.stem.LancasterStemmer()
                    features[(featname, st.stem(word))] = 1

            # Feature: Word Shape (of each word)
            if feature == "word_shape":
                for i,word in enumerate(sentence[ind].split()):
                    featname = 'word_shape-%d' % i
                    wordShapes = getWordShapes(word)
                    for j, shape in enumerate(wordShapes):
                        features[(featname + str(j), shape)] = 1

            # Feature: UMLS Semantic Type (for each word)
            if feature == 'umls_semantic_type_word':

                # Get a semantic type for each unigram
                for i,word in enumerate(sentence[ind]):
                    mapping = umls.umls_semantic_type_word(self.umls_lookup_cache , word )
                    # If is at least one semantic type
                    featname = 'umls_semantic_type_word-%d' % i
                    if mapping:
                        for concept in mapping:
                            features[(featname, concept )] = 1
                    else:
                        features[(featname ,   None  )] = 1


            # Feature: UMLS Semantic Types
            if feature == 'umls_cui':

                # Get UMLS CUIs (could have multiple)
                cuis = umls.get_cui(self.umls_lookup_cache , word)

                # Add each CUI
                if cuis:
                    for cui in cuis:
                        features[(feature,cui)] = 1
                else:
                    features[(feature,None)] = 1
                

            # Feature: Part of Speech (of each word)
            if feature == "pos":
                tags = tags or nltk.pos_tag(split_sentence)
                for j,pos_tag in enumerate(tags[ind:ind+len(sentence[ind].split())]):
                    featname = 'pos-%d' % j
                    features[(featname, pos_tag[1])] = 1

            # Feature: Wordnet Stem (for each chunk)
            if feature == "stem_wordnet":
                tags = tags or nltk.pos_tag(sentence)
                morphy_tags = {
                    'NN': nltk.corpus.reader.wordnet.NOUN,
                    'JJ': nltk.corpus.reader.wordnet.ADJ,
                    'VB': nltk.corpus.reader.wordnet.VERB,
                    'RB': nltk.corpus.reader.wordnet.ADV}
                morphy_tags = [(w, morphy_tags.setdefault(t[:2], nltk.corpus.reader.wordnet.NOUN)) for w, t in tags]
                st = nltk.stem.WordNetLemmatizer()
                tag = morphy_tags[ind]
                features[(feature, st.lemmatize(*tag))] = 1

            # Feature: Test Result (for each chunk)
            if feature == "test_result":
                right = " ".join([w for w in sentence[ind:]])
                if self.is_test_result(right):
                    features[(feature, None)] = 1

            # Feature: UMLS semantic concext
            if feature == 'umls_semantic_context':

                # the umls definition of the largest string the word is in
                umls_semantic_context_mappings = umls.umls_semantic_context_of_words( self.umls_lookup_cache , sentence )

                #if there are no mappings
                if umls_semantic_context_mappings[ind] == None:
                    features[(feature,None)] = 1
                # there could be multiple contexts, iterate through the sublist
                else:
                    for mapping in umls_semantic_context_mappings[ind]:
                        for concept in mapping:
                            features[(feature,concept)] = 1

        return features




    # Features that will be added back in
    #
    # Currently not used for reversion back to original one-pass
    #
    # Removed from concept_features() for visual clarity
    def concept_features_currently_not_used_features(self):

            # Feature: the chunk itself
            if feature == 'chunk':
                features.update( { ('chunk',sentence[ind]) :  1 } )

            # Feature: Uncased unigrams
            if feature == 'unigram':
                for i,word in enumerate( sentence[ind].split() ):
                    featname = 'unigram-%d' % i
                    features.update( { (featname, word.lower()) :  1 } )

            # Feature: First four letters of each word
            if feature == 'first-four-letters':
                prefix_list = [ word[:4] for word in sentence[ind].split() ]
                for i,word in enumerate(prefix_list):
                    featname = 'first-four-letters-%d' % i
                    features.update( { (featname, word) :  1 } )





    mitre_features = {
        "INITCAP": r"^[A-Z].*$",
        "ALLCAPS": r"^[A-Z]+$",
        "CAPSMIX": r"^[A-Za-z]+$",
        "HASDIGIT": r"^.*[0-9].*$",
        "SINGLEDIGIT": r"^[0-9]$",
        "DOUBLEDIGIT": r"^[0-9][0-9]$",
        "FOURDIGITS": r"^[0-9][0-9][0-9][0-9]$",
        "NATURALNUM": r"^[0-9]+$",
        "REALNUM": r"^[0-9]+.[0-9]+$",
        "ALPHANUM": r"^[0-9A-Za-z]+$",
        "HASDASH": r"^.*-.*$",
        "PUNCTUATION": r"^[^A-Za-z0-9]+$",
        "PHONE1": r"^[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]$",
        "PHONE2": r"^[0-9][0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]$",
        "FIVEDIGIT": r"^[0-9][0-9][0-9][0-9][0-9]",
        "NOVOWELS": r"^[^AaEeIiOoUu]+$",
        "HASDASHNUMALPHA": r"^.*[A-z].*-.*[0-9].*$ | *.[0-9].*-.*[0-9].*$",
        "DATESEPERATOR": r"^[-/]$",
    }

    def is_test_result(self, context):
        # note: make spaces optional?
        regex = r"^[A-Za-z]+( )*(-|--|:|was|of|\*|>|<|more than|less than)( )*[0-9]+(%)*"
        if not re.search(regex, context):
            return re.search(r"^[A-Za-z]+ was (positive|negative)", context)
        return True

    # Try to get QANN features
    def is_meaurement(self, word):
        regex = r"^[0-9]*(unit(s)|cc|L|mL|dL)$"
        return re.search(regex, word)

    def is_directive(self, word):
        regex = r"^(q\..*|q..|PRM|bid|prm|p\..*)$"
        return re.search(regex, word)
  
    def is_date(self, word):
        regex = r'^(\d\d\d\d-\d\d-\d|\d\d?-\d\d?-\d\d\d\d?|\d\d\d\d-\d\d?-\d\d?)$'
        return re.search(regex,word)

    def is_volume(self, word):
        regex = r"^[0-9]*(ml|mL|dL)$"
        return re.search(regex, word)

    def is_weight(self, word):
        regex = r"^[0-9]*(mg|g|mcg|milligrams|grams)$"
        return re.search(regex, word)

    def is_size(self, word):
        regex = r"^[0-9]*(mm|cm|millimeters|centimeters)$"
        return re.search(regex, word)

    def is_prognosis_location(self, word):
        regex = r"^(c|C)[0-9]+(-(c|C)[0-9]+)*$"
        return re.search(regex, word)

    def has_problem_form(self, word):
        regex = r".*(ic|is)$"
        return re.search(regex, word)

    # checks for a definitive classification at the word level
    def get_def_class(self, word):
        test_terms = {
            "eval", "evaluation", "evaluations",
            "sat", "sats", "saturation",
            "exam", "exams",
            "rate", "rates",
            "test", "tests",
            "xray", "xrays",
            "screen", "screens",
            "level", "levels",
            "tox"
        }
        problem_terms = {
            "swelling",
            "wound", "wounds",
            "symptom", "symptoms",
            "shifts", "failure",
            "insufficiency", "insufficiencies",
            "mass", "masses",
            "aneurysm", "aneurysms",
            "ulcer", "ulcers",
            "trama", "cancer",
            "disease", "diseased",
            "bacterial", "viral",
            "syndrome", "syndromes",
            "pain", "pains"
            "burns", "burned",
            "broken", "fractured"
        }
        treatment_terms = {
            "therapy",
            "replacement",
            "anesthesia",
            "supplement", "supplemental",
            "vaccine", "vaccines"
            "dose", "doses",
            "shot", "shots",
            "medication", "medicine",
            "treament", "treatments"
        }
        if word.lower() in test_terms:
            return 1
        elif word.lower() in problem_terms:
            return 2
        elif word.lower() in treatment_terms:
            return 3
        return 0


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

