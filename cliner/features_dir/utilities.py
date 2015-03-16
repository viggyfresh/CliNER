######################################################################
#  CliCon - utilities.py                                             #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Miscellaneous tools for handling data.                   #
######################################################################


import re

def is_prose_sentence(sentence):

    """
    is_prose_sentence()

    Purpose: Determine if a sentence of text is 'prose'

    @param sentence A list of words
    @return         A boolean

    >>> is_prose_sentence(['Admission', 'Date', ':'])
    False
    >>> is_prose_sentence(['Hello', 'World', '.'])
    True
    """

    # Empty sentence is not prose
    if not sentence:
        return False

    if sentence[-1] == '.' or sentence[-1] == '?':
        return True
    elif sentence[-1] == ':':
        return False
    elif len(sentence) <= 5:
        return False
    elif is_at_least_half_nonprose(sentence):
        return True
    else:
        return False



# at_least_half_nonprose()
#
# input:  A sentence
# output: A bollean yes/no
def is_at_least_half_nonprose(sentence):

    count = len(  [ w  for  w  in  sentence  if is_prose_word(w) ]  )

    if count >= len(sentence)/2:
        return True
    else:
        return False



# prose_word()
#
# input:  A word
# output: Boolean yes/no
def is_prose_word(word):

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

