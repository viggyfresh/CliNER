######################################################################
#  CliCon - sentence_features.py                                     #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Isolate the model's sentence-level features              #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Apr. 27, 2014'



import nltk
import re
from sets import ImmutableSet
from wordshape import getWordShapes



# What modules are available

from read_config import enabled_modules




# Import feature modules

if enabled_modules.GENIA:
    from genia_features import GeniaFeatures

if enabled_modules.UMLS:
    from umls_features import UMLSFeatures

from word_features import WordFeatures




class SentenceFeatures:


    # Feature Enabling
    enabled_IOB_prose_sentence_features = ImmutableSet( [ 'pos', 'stem_wordnet', 'GENIA', 'prev', 'next', 'prev_3_pos'] )

    enabled_IOB_nonprose_sentence_features = ImmutableSet( ['prev_pos', 'pos', 'next_pos', 'test_result', 'prev', 'next','prev_3_pos'])

    enabled_concept_features = ImmutableSet( ['pos','stem_wordnet', 'test_result', 'word_shape','prev','next', "UMLS"])



    # Instantiate an Sentence object
    def __init__(self, data):

        # Word-level features module
        self.feat_word = WordFeatures()

        # Only run GENIA tagger if module is available
        if data and enabled_modules.GENIA:
            print 'GENIA module enabled'
            self.feat_genia = GeniaFeatures(data)

        # Only create UMLS cache if module is available
        if enabled_modules.UMLS:
            print 'UMLS module enabled'
            self.feat_umls = UMLSFeatures()





    # IOB_prose_features()
    #
    # input:  A sentence
    # output: A list of hash tables of features
    def IOB_prose_features(self, sentence):

        features_list = []
        flag = 0 

        # Get a feature set for each word in the sentence
        for i,word in enumerate(sentence):
            features_list.append( self.feat_word.IOB_prose_features(sentence,i) )


        # Only POS tag once
        pos_tagged = nltk.pos_tag(sentence)

        # Used for 'prev' and 'next' features
        ngram_features = [{} for i in range(len(features_list))]


        # Allow for particular features to be enabled
        for feature in self.enabled_IOB_prose_sentence_features:

            # Feature: Part of Speech
            if feature == 'pos':
                for (i,(_,pos)) in enumerate(pos_tagged):
                    features_list[i].update( { ('pos',pos) : 1} )


            # Feature: Previous 3 POSs
            if feature == 'prev_3_pos':
                for i in range(len(sentence)):

                    # Where to begin
                    if i-3 < 0:
                        begin = 0
                    else:
                        begin = i-3

                    # Go as far back as 3 tokens
                    pos_features = {}
                    for p in pos_tagged[begin:i]:
                        pos = p[1]
                        pos_features.update( {('prev_3_pos',pos) : 1} )
                    
                    # Update feature dict
                    features_list[i].update(pos_features)


            # GENIA features
            if enabled_modules.GENIA and (feature == 'GENIA'):

                genia_feat_list = self.feat_genia.features(sentence)

                #print '\n\n'
                #print genia_feat_list
                #print '\n\n'

                for i,feat_dict in enumerate(genia_feat_list):
                    features_list[i].update(feat_dict)
                

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



    # IOB_nonprose_features()
    #
    # input:  A sentence
    # output: A hash table of features
    def IOB_nonprose_features(self, sentence):

        # Get the GENIA features of the current sentence
        #    (not used for nonprose, but it keeps things aligned for the prose)
        # FIXME - Making seperate classes will fix this
        if enabled_modules.GENIA and 'GENIA' in self.enabled_IOB_prose_sentence_features:
            _ = self.feat_genia.features(sentence, False)

                
        # If sentence is empty
        #if not sentence: return {}

        features_list = []

        # Get a feature set for each word in the sentence
        for i,word in enumerate(sentence):
            features_list.append( self.feat_word.IOB_nonprose_features(sentence,i) )

        pos_tagged = nltk.pos_tag(sentence)


        # Allow for particular features to be enabled
        for feature in self.enabled_IOB_nonprose_sentence_features:

            # Feature: Previous POS
            if feature == 'prev_pos':
                for i in range(len(sentence)):
                    if i == 0:
                        features_list[0].update({('prev_POS','<START>')      :1})
                    else:
                        features_list[i].update({('prev_POS',pos_tagged[i-1]):1})


            # Feature: Part of Speech
            if feature == 'pos':
                for (i,(_,pos)) in enumerate(pos_tagged):
                    features_list[i].update( { ('pos',pos) : 1} )


            # Feature: Previous POS
            if feature == 'next_pos':
                for i in range(len(sentence)):
                    if i == len(sentence)-1:
                        features_list[-1].update({('prev_POS','<START>')     :1})
                    else:
                        features_list[i].update({('prev_POS',pos_tagged[i-1]):1})


            # Feature: Test Result (for each chunk)
            if feature == "test_result":
                for index, features in enumerate(features_list):
                    right = " ".join([w for w in sentence[index:]])
                    if self.feat_word.is_test_result(right):
                        features[(feature, None)] = 1


            # Feature: Previous 3 POSs
            if feature == 'prev_3_pos':
                for i in range(len(sentence)):

                    # Where to begin
                    if i-3 < 0:
                        begin = 0
                    else:
                        begin = i-3

                    # Go as far back as 3 tokens
                    pos_features = {}
                    for p in pos_tagged[begin:i]:
                        pos = p[1]
                        pos_features.update( {('prev_3_pos',pos) : 1} )
                    
                    # Update feature dict
                    features_list[i].update(pos_features)


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


        # Word-level features for each word of the chunk
        for i,w in enumerate(sentence[ind].split()):
            word_features = self.feat_word.concept_features(w)

            # Map suffix to each feature
            append1 = lambda k,v: ((k[0] + "-" + str(i), k[1]), v)
            appended_feats = { append1(k,v) for k,v in word_features.items() }

            features.update( appended_feats)


        # Allow for particular features to be enabled
        for feature in self.enabled_concept_features:

             # Features: UMLS features
            if (feature == "UMLS") and enabled_modules.UMLS:
                umls_features = self.feat_umls.concept_features_for_sentence(split_sentence)
                features.update(umls_features)


            # Feature: Part of Speech (of each word)
            if feature == "pos":
                tags = tags or nltk.pos_tag(split_sentence)
                for j,pos_tag in enumerate(tags[ind:ind+len(sentence[ind].split())]):
                    featname = 'pos' 
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
                if self.feat_word.is_test_result(right):
                    features[(feature, None)] = 1


        return features


