import nltk

from sets import ImmutableSet

from wordshape import *

sentence_features = ImmutableSet(["pos", "stem_wordnet", "test_result", "prev", "next"])
word_features = ImmutableSet(["word", "length", "mitre", "stem_porter", "stem_lancaster", "word_shape"])
enabled_features = sentence_features | word_features

    # input:  A sentence from a medical text file (list of words)
    # output: A list of hash tables
def features_for_sentence(sentence):
    features_list = []

    for word in sentence:
        features_list.append(features_for_word(word))

    tags = None
    for feature in sentence_features:
        if feature not in enabled_features:
            continue

        if feature == "pos":
            tags = tags or nltk.pos_tag(sentence)
            for i, features in enumerate(features_list):
                tag = tags[i][1]
                features[(feature, tag)] = 1

        if feature == "stem_wordnet":
            tags = tags or nltk.pos_tag(sentence)
            morphy_tags = {
                'NN': nltk.corpus.reader.wordnet.NOUN,
                'JJ': nltk.corpus.reader.wordnet.ADJ,
                'VB': nltk.corpus.reader.wordnet.VERB,
                'RB': nltk.corpus.reader.wordnet.ADV}
            morphy_tags = [(w, morphy_tags.setdefault(t[:2], nltk.corpus.reader.wordnet.NOUN)) for w, t in tags]
            st = nltk.stem.WordNetLemmatizer()
            for i, features in enumerate(features_list):
                tag = morphy_tags[i]
                features[(feature, st.lemmatize(*tag))] = 1

        if feature == "test_result":
            for index, features in enumerate(features_list):
                right = " ".join([w for w in sentence[index:]])
                if is_test_result(right):
                    features[(feature, None)] = 1


    ngram_features = [{} for i in range(len(features_list))]
    if "prev" in enabled_features:
        prev = lambda f: {("prev_"+k[0], k[1]): v for k, v in f.items()}
        prev_list = map(prev, features_list)
        for i in range(len(features_list)):
            if i == 0:
                ngram_features[i][("prev", "*")] = 1
            else:
                ngram_features[i].update(prev_list[i-1])

    if "next" in enabled_features:
        next = lambda f: {("next_"+k[0], k[1]): v for k, v in f.items()}
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



    # input:  a single word, like
    #         Admission
    # output: A hash table of features
    #         features include: word, length, mitre, stem_porter
def features_for_word( word):
    features = {'dummy': 1}  # always have >0 dimensions

            # word_shape, word, length, mitre, stem_porter, stem_lancaster
    for feature in word_features:

                    # word_shape, test_result, word, pos, next, length, stem_wordnet, mitre, stem_porter, prev, stem_lancaster
        if feature not in enabled_features:
            continue

        if feature == "word":
            features[(feature, word)] = 1

        if feature == "length":
            features[(feature, None)] = len(word)

        if feature == "mitre":
            for f in mitre_features:
                if re.search(mitre_features[f], word):
                    features[(feature, f)] = 1

        if feature == "stem_porter":
            st = nltk.stem.PorterStemmer()
            features[(feature, st.stem(word))] = 1

        if feature == "stem_lancaster":
            st = nltk.stem.LancasterStemmer()
            features[(feature, st.stem(word))] = 1

        if feature == "stem_snowball":
            st = nltk.stem.SnowballStemmer("english")
            #features[(feature, st.stem(word))] = 1

        if feature == "word_shape":
            wordShapes = getWordShapes(word)
            for i, shape in enumerate(wordShapes):
                features[(feature + str(i), shape)] = 1

        if feature == "metric_unit":
            unit = 0
            if is_weight(word):
                unit = 1
            elif is_size(word):
                unit = 2
            features[(feature, None)] = unit

        # look for prognosis locaiton
        #if feature == "radial_loc":
        # THIS MIGHT BE BUGGED
        #    if is_prognosis_location(word):
        #        features[(feature, None)] = 1

        if feature == "has_problem_form":
            if has_problem_form(word):
                features[(feature, None)] = 1

        if feature == "def_class":
            features[(feature, None)] = get_def_class(word)

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

def is_test_result( context):
    # note: make spaces optional?
    regex = r"^[A-Za-z]+( )*(-|--|:|was|of|\*|>|<|more than|less than)( )*[0-9]+(%)*"
    if not re.search(regex, context):
        return re.search(r"^[A-Za-z]+ was (positive|negative)", context)
    return True

def is_weight( word):
    regex = r"^[0-9]*(mg|g|milligrams|grams)$"
    return re.search(regex, word)

def is_size( word):
    regex = r"^[0-9]*(mm|cm|millimeters|centimeters)$"
    return re.search(regex, word)

def is_prognosis_location( word):
    regex = r"^(c|C)[0-9]+(-(c|C)[0-9]+)*$"
    return re.search(regex, word)

def has_problem_form( word):
    regex = r".*(ic|is)$"
    return re.search(regex, word)

# checks for a definitive classification at the word level
def get_def_class( word):
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
