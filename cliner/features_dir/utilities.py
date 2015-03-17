######################################################################
#  CliCon - utilities.py                                             #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Miscellaneous tools for handling data.                   #
######################################################################


import re
import cPickle as pickle

def load_pickled_obj(path_to_pickled_obj):

    data = ""

    with open(path_to_pickled_obj, "rb") as f:

        for line in f:
            data += line

        return pickle.loads(data)

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

