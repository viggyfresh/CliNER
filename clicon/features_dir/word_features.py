######################################################################
#  CliCon - word_features.py                                         #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Isolate all word-level features into a single file       #
######################################################################




__author__ = 'Willie Boag'
__date__   = 'Apr 27, 2014'



import nltk
import re
from sets import ImmutableSet
from wordshape import getWordShapes
    



class WordFeatures:

    #enabled_IOB_prose_word_features = ImmutableSet( ['Generic#', 'last_two_letters', 'word', 'length', 'mitre', 'stem_porter', 'stem_lancaster', 'word_shape', 'metric_unit' ] )
    enabled_IOB_prose_word_features = []

    enabled_IOB_nonprose_word_features = ImmutableSet( ['word', 'word_shape', 'metric_unit', 'mitre', 'directive', 'date' ] )

    enabled_concept_features = ImmutableSet( ['word', 'prefix', 'stem_porter', 'stem_lancaster', 'previous_word_stem', 'next_word_stem'] )


    def __init__(self):

        self.enabled_IOB_prose_word_features.append('word')
        self.enabled_IOB_prose_word_features.append('Generic#')
        #self.enabled_IOB_prose_word_features.append('last_two_letters')
        #self.enabled_IOB_prose_word_features.append('length')
        #self.enabled_IOB_prose_word_features.append('mitre')
        #self.enabled_IOB_prose_word_features.append('stem_porter')
        #self.enabled_IOB_prose_word_features.append('stem_lancaster')
        #self.enabled_IOB_prose_word_features.append('word_shape')

        pass


    # IOB_prose_features_for_word()
    #
    # input:  A single word
    # output: A dictionary of features
    def IOB_prose_features(self, word):

        # Feature: <dummy>
        features = {('dummy', None): 1}  # always have >0 dimensions
  
        # Allow for particular features to be enabled
        for feature in self.enabled_IOB_prose_word_features:

            if feature == "stem_lancaster":
                st = nltk.stem.LancasterStemmer()
                features[ (feature, st.stem(word.lower())) ] = 1

            if feature == "word":
                w = word.lower()
                features[(feature, w)] = 1

            # Feature: Generic# stemmed word
            if feature == 'Generic#':
                generic = re.sub('[0-9]','0',word)
                features[ ('Generic#',generic) ] = 1

            # Feature: Last two leters of word
            if feature == 'last_two_letters':
                features[ ('last_two_letters',word[-2:]) ] = 1


            if feature == "length":
                features[(feature, None)] = len(word)

            if feature == "mitre":
                for f in self.mitre_features:
                    if re.search(self.mitre_features[f], word):
                        features[(feature, f)] = 1

            if feature == "stem_porter":
                st = nltk.stem.PorterStemmer()
                features[(feature, st.stem(word))] = 1

            if feature == "word_shape":
                wordShapes = getWordShapes(word)
                for shape in wordShapes:
                    features[(feature, shape)] = 1


        return features





    # IOB_nonprose_features_for_word()
    #
    # input:  A single word
    # output: A dictionary of features
    def IOB_nonprose_features(self, word):

        # Feature: <dummy>
        features = {'dummy': 1}  # always have >0 dimensions

        enabled = True

        # Allow for particular features to be enabled
        for feature in self.enabled_IOB_nonprose_word_features:

            # Feature: The word, itself
            if feature == 'word':
                features[('word', word.lower())] = 1


            # Feature: Metric Unit
            if feature == "metric_unit":
                unit = None
                if self.is_weight(word):
                    unit = 'weight'
                elif self.is_size(word):
                    unit = 'size'
                elif self.is_volume(word):
                    unit = 'volume'
                features[('metric_unit',unit)] = 1


            # Feature: Date
            if feature == 'date':
                if self.is_date(word):
                    features[('date',None)] = 1


            # Feature: Directive
            if feature == 'directive':
                if self.is_directive(word):
                    features[('directive',None)] = 1


            # Feature: Mitre
            if feature == "mitre":
                for f in self.mitre_features:
                    if re.search(self.mitre_features[f], word):
                        features[('mitre', f)] = 1


            # Feature: Word Shape
            if feature == "word_shape":
                wordShapes = getWordShapes(word)
                for shape in wordShapes:
                    features[('word_shape', shape)] = 1

        return features



    def concept_features_for_word(self, word):

        """
        concept_features_for_word()
 
        @param  word. A word to generate features for
        @return       A dictionary of features
        """

        features = {}

        # Allow for particular features to be enabled
        for feature in self.enabled_concept_features:

            # Feature: Uncased Word
            if feature == "word":
                features[ ("word",word.lower()) ] = 1

            # Feature: Porter Stem
            if feature == "stem_porter":
                st = nltk.stem.PorterStemmer()
                features[ ("stem_poter", st.stem(word)) ] = 1

            # Feature: Lancaster Stem
            if feature == "stem_lancaster":
                st = nltk.stem.LancasterStemmer()
                features[ ("stem_lancaster", st.stem(word)) ] = 1

            # Feature: First Four Letters
            if feature == "prefix":
                prefix = word[:4].lower()
                features[ ("prefix",prefix) ] = 1



            # Feature: Length
            if feature == "length":
                features[ ("length",None) ] = len(word)

            # Feature: Mitre
            if feature == "mitre":
                for f in self.mitre_features:
                    if re.search(self.mitre_features[f], word):
                        features[ ("mitre",f) ] = 1

            # Feature: Word Shape
            if feature == "word_shape":
                wordShapes = getWordShapes(word)
                for shape in wordShapes:
                    features[ ("word_shape", shape) ] = 1


        return features




    def concept_features_for_chunk(self, sentence, ind):

        """
        concept_features_for_chunk()
 
        @param  word. A chunk from the sentence
        @return       A dictionary of features
        """

        features = {'dummy':1}

        # Word-level features for each word of the chunk
        for w in sentence[ind].split():
            word_features = self.concept_features_for_word(w)
            features.update(word_features)


        # Stemmer
        st = nltk.stem.PorterStemmer()


        # Context windows
        for feature in self.enabled_concept_features:

            # Feature: Previous word
            if feature == "previous_word_stem":
                if ind != 0:
                    prev_ind = ind - 1
                    prev_chunk = sentence[prev_ind].split()
                    prev_word = st.stem( prev_chunk[-1] )
                    features[ ('prev_word_stem',prev_word) ] = 1
                else:
                    features[ ('prev_word_stem',None) ] = 1

            # Feature: Previous word
            if feature == "previous_word_stem":
                if ind != len(sentence)-1:
                    next_ind = ind + 1
                    next_chunk = sentence[next_ind].split()
                    next_word = st.stem( next_chunk[-1] )
                    features[ ('next_word_stem',next_word) ] = 1
                else:
                    features[ ('next_word_stem',None) ] = 1


        return features




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
        regex= r'^(\d\d\d\d-\d\d-\d|\d\d?-\d\d?-\d\d\d\d?|\d\d\d\d-\d\d?-\d\d?)$'
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

