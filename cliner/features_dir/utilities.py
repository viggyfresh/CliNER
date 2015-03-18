######################################################################
#  CliCon - utilities.py                                             #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Miscellaneous tools for handling data.                   #
######################################################################


import re
import cPickle as pickle
import nltk.data, nltk.tag
import os

# used as a default path for stashing pos tagger.
pos_tagger_path = os.path.join( os.environ['CLINER_DIR'], "cliner/features_dir/nltk_tagger.p")

def load_pickled_obj(path_to_pickled_obj):

    data = None

    with open(path_to_pickled_obj, "rb") as f:

        data = f.read()

    return pickle.loads(data)

def pickle_dump(obj, path_to_obj):

    f = open(path_to_obj, "wb")

    pickle.dump(obj, f)

    f.close()

def dump_pos_tagger(path_to_obj):

    tagger = nltk.data.load(nltk.tag._POS_TAGGER)

    pickle_dump(tagger, path_to_obj)

def load_pos_tagger(path_to_obj=pos_tagger_path):
    """ faster tagger loading """

    tagger = None

    if os.path.isfile(path_to_obj):

        print "loading tagger..."

        tagger = load_pickled_obj(path_to_obj)

    else:

        print "tagger not currently stashed... creating new stash..."

        dump_pos_tagger(path_to_obj)

        tagger = load_pickled_obj(path_to_obj)

    return tagger

# prose_sentence()
#
# input:  A sentence
# output: Boolean yes/no
def prose_sentence(sentence):

    # Empty sentence is not prose
    if not sentence:
        return False

    if sentence[-1] == '.' or sentence[-1] == '?':
        return True
    elif sentence[-1] == ':':
        return False
    elif len(sentence) <= 5:
        return False
    elif at_least_half_nonprose(sentence):
        return True
    else:
        return False



# at_least_half_nonprose()
#
# input:  A sentence
# output: A bollean yes/no
def at_least_half_nonprose(sentence):

    count = len(  [ w  for  w  in  sentence  if prose_word(w) ]  )

    if count >= len(sentence)/2:
        return True
    else:
        return False



# prose_word()
#
# input:  A word
# output: Boolean yes/no
def prose_word(word):

    # Punctuation
    for punc in ".?,!:\"'":
        if punc in word:
            return False

    # Digit
    if re.match('\d', word):
        return False

    # All uppercase
    if word == word.upper():
        return False

    # Else
    return True


#EOF
