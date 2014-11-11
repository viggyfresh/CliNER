from __future__ import with_statement


######################################################################
#  CliNER - note_i2b2.py                                             #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Derived note object for reading i2b2 formatted data.     #
######################################################################


__author__ = 'Willie Boag'
__date__   = 'Nov. 6, 2014'



import re
import string
from copy import copy
import nltk.data
import os.path

from abstract_note import AbstractNote
from utilities_for_notes import classification_cmp


class Note_i2b2(AbstractNote):

    def __init__(self):
        # Internal representation natural for i2b2 format
        self.data            = []  # list of list of tokens
        self.classifications = []  # list of concept tuples
        self.line_inds       = []  # list of (start,end) indices for every line


    def getExtension(self):
        return 'con'


    def getTokenizedSentences(self):
        return self.data


    def getClassificationTuples(self):

        # return value
        retVal = []

        # Build list of standardized classification tuples
        for classification in self.classifications:
            concept,lineno,tok_start,tok_end = classification

            # character offset of beginning of line
            begin = self.line_inds[lineno-1][0]

            # Sweep through line to get character offsets from line start
            start = 0
            for word in self.data[lineno-1][:tok_start]:
                start += len(word) + 1

            # Length of concept span
            end = start
            for word in self.data[lineno-1][tok_start:tok_end+1]:
                end += len(word) + 1
            end -= 1

            #print begin
            #print begin+start, begin+end
            #print '~~' + self.text[begin+start:begin+end] + '~~'

            retVal.append( (concept,[(begin+start,begin+end)]) )

        return retVal


    def getLineIndices(self):
        return self.line_inds


    def read_standard(self, txt, con=None):

        # Helper function
        def lineno_and_tokspan(char_span):
            """ File character offsets => line number and index into line """
            for i,span in enumerate(self.line_inds):
                if char_span[1] <= span[1]:

                    #print "span: ", span

                    # start and end of span relative to sentence
                    start = char_span[0] - span[0]
                    end   = char_span[1] - span[0]

                    #print "START: ", start
                    #print "END: ", end

                    #print "USING span on self.text: ", self.text[span[0]:span[1]]
                    #print "USING start and end: ", self.text[span[0]:span[1]][start:end]

                    #print "self.data", self.data[i]
                    tok_span = [0,len(self.data[i])-1]
                    char_count = 0

                    dataWithEmptyChars = re.split(" |\n|\t", self.text[span[0]:span[1] + 1])

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
                    #print self.data[i][tok_span[0]:tok_span[1]]
                    #print

                    # return line number AND token span
                    #print "LINE: ", i
                    #print "TOK SPAN: ", tok_span
                    #print self.data[i]
                    #print tok_span

                    #print "USING char_span on self.text: ", self.text[char_span[0]:char_span[1]]
                    #print "USING tok_span on self.data[i]", self.data[i][tok_span[0]], self.data[i][tok_span[1]]
                    #print "USING char_span on self.text: ", self.text[char_span[0]], self.text[char_span[1]]


                    return (i, tuple(tok_span))

            return None


        start = 0
        end = 0

        with open(txt) as f:

            # Get entire file
            text = f.read()
            self.text = text

            # Split into lines
            self.data = map(lambda s: s.split(), text.split('\n'))

            # Tokenize each sentence into words (and save line number indices)
            toks = []
            gold = []          # Actual lines

            for sent in self.data:

                gold.append(sent)

                # Keep track of which indices each line has
                for word in sent:
                    end += len(word) + 1

                self.line_inds.append( (start,end-1) )
                start = end

                # Skip ahead to next non-whitespace
                while (start < len(text)) and text[start].isspace(): start += 1


        # If an accompanying concept file was specified, read it
        if con:
            classifications = []
            with open(con) as f:
                for line in f:

                    # Empty line
                    if line == '\n': continue

                    # Parse concept file line
                    fields = line.strip().split('||')
                    #print fields
                    concept = fields[0]
                    span_inds = []
                    for i in range(1,len(fields),2):
                        span = int(fields[i]), int(fields[i+1])
                        span_inds.append( span )

                    # FIXME - For now, treat non-contiguous spans as separate
                    for span in span_inds:
                        # Add the classification to the Note object
                        l,(start,end) = lineno_and_tokspan(span)
                        #print 'span:   ', span
                        #print 'lineno: ', l
                        #print 'start:  ', start
                        #print 'end:    ', end
                        #print '\n'
                        classifications.append((concept,l+1,start,end))

            # Safe guard against concept file having duplicate entries
            classifications = list(set(classifications))

            # Concept file does not guarantee ordering by line number
            self.classifications = sorted(classifications,cmp=classification_cmp)



    def read(self, txt, con=None):
        """
        Note_i2b2::read()
       
        @param txt. A file path for the tokenized medical record
        @param con. A file path for the i2b2 annotated concepts for txt
        """

        # Character indices of each line
        start = 0
        end = 0

        # Read in the medical text
        with open(txt) as f:

            # Original text file
            self.text = f.read()

            i = 0
            for line in self.text.split('\n'):
                end += len(line) + 1
                self.line_inds.append( (start,end-1) )
                start = end

                # Strip away non-printable characters
                line = filter(lambda x: x in string.printable, line)

                # Add sentence to the data list
                self.data.append(line.split())

        # TEST - is line_inds correct?
        #print self.line_inds
        #i = 0
        #for line,span in zip(self.data,self.line_inds):
        #    start,end = span
        #    print '<t>' + self.text[start:end] + '</t>'
        #    print '<l>' + ' '.join(line)       + '</l>'
        #    print
        #    i += 1
        #    if i == 10: exit()

        # If an accompanying concept file was specified, read it
        if con:
            classifications = []
            with open(con) as f:
                for line in f:

                    # Empty line
                    if line == '\n': continue

                    # concept
                    prefix, suffix = line.split('||')
                    text = prefix.split()
                    conc = suffix[3:-2]

                    start = text[-2].split(':')
                    end   = text[-1].split(':')

                    assert "concept spans one line", start[0] == end[0]

                    # lineno
                    l = int(start[0])

                    # starttok
                    # endtok
                    start = int(start[1])
                    end   = int(  end[1])

                    # Add the classification to the Note object
                    classifications.append( (conc,l,start,end) )

                    #print "txt:   ", txt
                    #print "l:     ", l
                    #print "start: ", start
                    #print "end:   ", end
                    #print "line:  ", self.data[l-1]

                    #print "\n" + "-" * 80

            # Safe guard against concept file having duplicate entries
            classifications = list(set(classifications))

            # Concept file does not guarantee ordering by line number
            self.classifications = sorted(classifications, 
                                          cmp=classification_cmp)


    def write(self, labels=None):

        """
        Note_i2b2::write()
        
        Purpose: Return the given concept label predictions in i2b2 format
        
        @param  labels. A list of classifications
        @return         A string of i2b2-concept-file-formatted data
        """

        # Return value
        retStr = ''

        # List of list of words (line-by-line)
        tlist = self.data


        # If given labels to write, use them. Default to self.classifications
        if labels != None:
            classifications = labels
        elif self.classifications != None:
            classifications = self.classifications
        else:
            raise Exception('Cannot write concept file: must specify labels')


        # For each classification
        for classification in classifications:

            # Ensure 'none' classifications are skipped
            if classification[0] == 'none':
                raise('Classification label "none" should never happen')

            concept = classification[0]
            lineno  = classification[1] 
            start   = classification[2]
            end     = classification[3]

            # A list of words (corresponding line from the text file)
            text = tlist[lineno-1]

            #print "\n" + "-" * 80
            #print "classification: ", classification
            #print "lineno:         ", lineno
            #print "start:          ", start
            #print "end             ", end
            #print "text:           ", text
            #print "text[start]:    ", text[start]
            #print "concept:        ", concept

            # The text string of words that has been classified
            datum = text[start]
            for j in range(start, end):
                datum += " " + text[j+1] 

            # Line:TokenNumber of where the concept starts and ends
            idx1 = "%d:%d" % (lineno, start)
            idx2 = "%d:%d" % (lineno, end  )

            # Classification
            label = concept

            # Fixing issue involving i2b2 format (remove capitalization)
            lowercased = [w.lower() for w in datum.split()]
            datum = ' '.join(lowercased)

            # Print format
            retStr +=  "c=\"%s\" %s %s||t=\"%s\"\n" % (datum, idx1, idx2, label)

        # return formatted data
        return retStr

