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
    
# What modules are available
from read_config import enabled_modules


if enabled_modules.UMLS:
    from umls_features import UMLSFeatures


class WordFeatures:

    enabled_IOB_prose_word_features = ImmutableSet( ['Generic#', 'last_two_letters', 'word', 'length', 'mitre', 'stem_porter', 'word_shape', 'metric_unit', 'UMLS' ] )

    enabled_IOB_nonprose_word_features = ImmutableSet( ['word', 'uncased_prev_word', 'word_shape', 'metric_unit', 'mitre', 'directive' ] )

    enabled_concept_word_features = ImmutableSet( ['word', 'length', 'mitre', 'stem_porter', 'stem_lancaster', 'word_shape', 'UMLS'] )


    def __init__(self):

        # Only use UMLS feature module if it is available
        if enabled_modules.UMLS:
            self.feat_umls = UMLSFeatures()



    # IOB_prose_features_for_word()
    #
    # input:  A single word
    # output: A dictionary of features
    def IOB_prose_features(self, sentence, ind):

        # Abbreviation for most features,
        #    although some will require index for context
        word = sentence[ind]


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
                    features.update( {('prev_word', sentence[ind-1]) : 1} )

            # Feature: UMLS Word Features (only use prose ones)
            if (feature == "UMLS") and enabled_modules.UMLS:
                umls_features = self.feat_umls.IOB_prose_features(word)
                features.update( umls_features )


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





    # IOB_nonprose_features_for_word()
    #
    # input:  A single word
    # output: A dictionary of features
    def IOB_nonprose_features(self, sentence, ind):

        # Abbreviation for most features,
        #    although some will require index for context
        word = sentence[ind]


        # Feature: <dummy>
        features = {'dummy': 1}  # always have >0 dimensions


        # Allow for particular features to be enabled
        for feature in self.enabled_IOB_nonprose_word_features:

            # Feature: The word, itself
            if feature == 'word':
                features.update( { ('word',word.lower()) : 1} )

            # Feature: Uncased previous word
            if feature == 'uncased_prev_word':
                if ind == 0:
                   features.update( {('uncased_prev_word','<START>'            ) : 1} )
                else:
                    features.update( {('uncased_prev_word',sentence[ind-1].lower()) : 1} )


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
                features[(feature, unit)] = 1


            # Feature: Date
            if feature == 'date':
                if self.is_date(word):
                    features[feature] = 1


            # Feature: Directive
            if feature == 'directive':
                if self.is_directive(word):
                    features[feature] = 1


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


            # Feature: UMLS Word Features (only use nonprose ones)
            if (feature == "UMLS") and enabled_modules.UMLS:
                umls_features = self.feat_umls.IOB_nonprose_features(word)
                features.update( umls_features )


        return features



    def concept_features(self, word):

        """
        concept_features_for_word()
 
        @param  word. A word to generate features for
        @return       A dictionary of features
 
        NOTE: Currently does not involve context (AKA prev).
              In order to support context, you'd need to change arg from
               'word'  ->  'chunk' and 'ind'
        """

        features = {}

        # Allow for particular features to be enabled
        for feature in self.enabled_concept_word_features:

            # Feature: Word (each word)
            if feature == "word":
                features[ ("word",word) ] = 1

            # Feature: Length (of each word)
            if feature == "length":
                features[ ("length",None) ] = len(word)

            # Feature: Mitre (of each word)
            if feature == "mitre":
                for f in self.mitre_features:
                    if re.search(self.mitre_features[f], word):
                        features[ ("mitre",f) ] = 1

            # Feature: Porter Stem (of each word)
            if feature == "stem_porter":
                st = nltk.stem.PorterStemmer()
                features[ ("stem_poter", st.stem(word)) ] = 1

            # Feature: Lancaster Stem (of each word)
            if feature == "stem_lancaster":
                st = nltk.stem.LancasterStemmer()
                features[ ("stem_lancaster", st.stem(word)) ] = 1

            # Feature: Word Shape (of each word)
            if feature == "word_shape":
                wordShapes = getWordShapes(word)
                for j, shape in enumerate(wordShapes):
                    features[ ("word_shape" + str(j), shape) ] = 1

            # Features: UMLS Features
            if (feature == "UMLS") and enabled_modules.UMLS:
                umls_features = self.feat_umls.concept_features_for_word(word)
                features.update(umls_features)


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

