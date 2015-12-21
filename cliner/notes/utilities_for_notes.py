######################################################################
#  CliNER - utilities.py                                             #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Helper tools for Note objects                            #
######################################################################


import nltk.data
import nltk.tokenize
import re
import string


nltk_sent_tokenizer = nltk.tokenize.PunktSentenceTokenizer()
nltk_word_tokenizer = nltk.tokenize.WordPunctTokenizer()



class NoteException(Exception):
    pass


def classification_cmp(a,b):
    """
    concept_cmp()

    Purpose: Compare concept classification tokens
    """
    a = (int(a[1]), int(a[2]))
    b = (int(b[1]), int(b[2]))

    # Sort by line number
    if a[0] < b[0]:
        return -1
    if a[0] > b[0]:
        return  1
    else:
        # Resolve lineno ties with indices
        if a[1] < b[1]:
            return -1
        if a[1] > b[1]:
            return  1
        else:
            if a[2] < b[2]:
                return -1
            if a[2] > b[2]:
                return  1
            else:
                return 0



def concept_cmp(a,b):
    """
    concept_cmp()

    Purpose: Compare concept classification tokens
    """
    return a[1][0] < b[1][0]



# Helper function
def lineno_and_tokspan(line_inds, data, text, char_span):
    """ File character offsets => line number and index into line """

    #q = False
    #if q:
    #    print '\n\n\n'
    #    print 'char_span: ', char_span
    #    print '<<%s>>' % text[char_span[0]:char_span[1]]

    # Locate line number
    for i,candidate_span in enumerate(line_inds):
        if char_span[1] <= candidate_span[1]:
            lineno = i
            break

    phrase = text[char_span[0]:char_span[1]]
    #if q:
    #    print
    #    print 'PHRASE: <%s>' % phrase
    #    print

    tokenized = data[lineno]
    #if q:
    #    print
    #    print 'TOKENIZED: ', tokenized
    #    print

    # TODO make test case that has a false alarm token sequence

    # Try to find token sequence that covers phrase
    buf = phrase.strip()
    #print '\tinitial buf: <%s>\n' % buf
    tokens = []
    i = 0
    while i < len(tokenized):
        token = tokenized[i]
        #if q:
        #    print '\ti: ', i
        #    print '\tbuf: <%s>' % buf
        #    print '\ttok: <%s>' % token
        #    print
        if buf.startswith(token):
            buf = buf[len(token):].strip()
            #if q:
            #    print '\t\tnew buf: <%s>' % buf
            tokens.append(i)
            #if q:
            #    print '\t\ttokens:  ', tokens
            #    print
            if len(buf) == 0:
                # Verify that this is the right span
                tokspan = (tokens[0], tokens[-1])
                span = lno_and_tokspan__to__char_span(line_inds,data,text,lineno,tokspan)
                #if q:
                #    print '\t\ttarget:    ', char_span
                #    print '\t\tcandidate: ', span
                #    print '\t\tchar_span text: <%s>' % text[char_span[0]:char_span[1]]
                # If this is the wrong span, then reset
                if span != char_span:
                    buf = phrase.strip()
                    while len(tokens) > 0:
                        i -= 1
                        tokens.pop()
                    i += 1
                else:
                    break

        else:
            # Reset buffer
            buf = phrase.strip()

            # Backtrack (Mealy model)
            while len(tokens) > 0:
                i -= 1
                tokens.pop()
        i += 1

    #print 'tokens: ', tokens
    start_tok = tokens[ 0]
    end_tok   = tokens[-1]

    return lineno, (start_tok,end_tok)




# Helper function
def __old_lineno_and_tokspan(line_inds, data, text, char_span):
    """ File character offsets => line number and index into line """
    for i,span in enumerate(line_inds):
        if char_span[1] <= span[1]:

            #print
            #print "span: ", span

            # start and end of span relative to sentence
            start = char_span[0] - span[0]
            end   = char_span[1] - span[0]

            #print "START: ", start
            #print "END: ", end

            #print "USING span on text: ~" + text[span[0]:span[1]] + '~'
            #print "USING start and end: ~" + text[span[0]:span[1]][start:end]+'~'

            #print "data", data[i]
            tok_span = [0,len(data[i])-1]
            char_count = 0

            dataWithEmptyChars = re.split(" |\n|\t", text[span[0]:span[1] + 1])

            index = 0
            for j,tok in enumerate(dataWithEmptyChars):
                if char_count > end:
                    tok_span[1] = index -1
                    break
                elif char_count == start:
                    tok_span[0] = index
                char_count += len(tok) + 1
                if len(tok) > 0:
                   index += 1
                #print '\t',j, '\t', tok, '(', char_count, ')'

            #print start, end
            #print tok_span
            #print text[span[0]:span[1]]
            #print data[i][tok_span[0]:tok_span[1]]
            #print

            # return line number AND token span
            #print "LINE: ", i
            #print "TOK SPAN: ", tok_span
            #print data[i]
            #print tok_span

            #print "USING char_span on text: ", text[char_span[0]:char_span[1]]
            #print "USING tok_span on data[i]", data[i][tok_span[0]], data[i][tok_span[1]]
            #print "USING char_span on text: ", text[char_span[0]], text[char_span[1]]

            return (i, tuple(tok_span))

    return None




# Helper function
def lno_and_tokspan__to__char_span(line_inds, data, text, lineno, tokspan):
    """ File character offsets => line number and index into line """
    # NOTE - makes no assumptions about what joins the tokens in the span

    # Get char offsets for that sentence
    #print '\n\n\n'
    #print 'lineno: ', lineno
    #print 'toks:   ', tokspan
    start,end = line_inds[lineno]
    phrase = text[start:end]
    #print 'start: ', start
    #print 'end:   ', end

    # Get the list of tokens for that sentence
    start_tok,end_tok = tokspan
    toks = data[lineno][start_tok:end_tok+1]

    phrase = phrase.replace('\n', '\t')
    #print '\tphrase: <%s>' % phrase
    #print '\ttarget toks: ' ,toks

    tokens = data[lineno]
    buf = phrase
    index = 0
    for i in range(1,start_tok+1):
        index += len(tokens[i-1])
        index += buf[index:].index(tokens[i])
        #print '\t\ttok: ', tokens[i]
        #print '\t\t\tindex: ', index
        #low = max(0,index-30)
        #print '\t\t\tbuf[:index]: <%s>' % buf[low:index]
    start_ind = index
    #print '\tstart_ind: ', start_ind

    #print '\n'*5
    #print 'start: <%s>' % phrase[start_ind:]
    #print '\n'*5

    for i in range(start_tok+1,end_tok+1):
        index += len(tokens[i-1])
        index += buf[index:].index(tokens[i])
        #print '\t\ttok: ', tokens[i]
        #print '\t\t\tindex: ', index
        #low = max(0,index-30)
        #print '\t\t\tbuf[:index]: <%s>' % buf[low:index]
    end_ind = index + len(tokens[end_tok])
    #print '\tend_ind:   ', end_ind

    #print '\n'*5
    #print 'finale: <%s>' % phrase[start_ind:end_ind]
    #print '\n'*5

    final_span = (start+start_ind, start+end_ind)
    return final_span




# Break file into sentences.
class SentenceTokenizer:

    def __init__(self):
        self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    #def tokenize(self, text_file):
    def tokenize(self, text):
        """ Split the document into sentences """
        #return text.split('\n')
        #return self.sent_tokenizer.tokenize(text)
        text = re.sub('\n\n+', '\n\n', text)
        data = self.sent_tokenizer.tokenize(text)

        splitted = [ sent.split('\n\n') for sent in data  ]
        sents = sum(splitted, [])

        # Could do something (similar to here) to ensure nonprose is split well
        #splitted = [ sent.split(':')    for sent in sents ]
        #sents = sum(splitted, [])

        return [ sent.strip() for sent in sents if (sent.strip() != []) ]

    def span_tokenize(self, text):
        spans = nltk_sent_tokenizer.span_tokenize(text)
        for span in spans:
            start,end = span
            print '[[[%s]]]' % text[start:end+1]
        print spans



# Break sentence into words
class WordTokenizer:

    # TODO - PunktWordTokenizer (http://www.nltk.org/api/nltk.tokenize.html)
    def __init__(self):
        pass

    def tokenize(self, sent):
        """ Split the sentence into tokens """
        #return sent.strip().split()
        #return sent.strip().split(' ')
        #return filter(lambda word: word!= '', nltk.tokenize.wordpunct_tokenize(sent))
        toks = filter(lambda w: len(w)>0, nltk.tokenize.wordpunct_tokenize(sent))
        #splitted = [ w.replace('/',' / ').split() for w in toks ]
        #toks = sum(splitted, [])
        return toks

    def span_tokenize(self, sent):
        raise 'TODO: WordTokenizer::span_tokenize()'
        #toks = filter(lambda w: len(w)>0, nltk.tokenize.wordpunct_tokenize(sent))
        return spans



def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)

