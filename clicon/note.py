from __future__ import with_statement

import re
from copy import copy


class Note:

    # Constructor
    def __init__(self):
        # data     - A list of list of words
        # concepts - A one-to-one correspondence of each word's concept
        # classifications - A list of tuples that convey concept labels
        # boundaries      - A one-to-one correspondence of each word's BIO status
        self.data            = []
        self.concepts        = []
        self.classifications = []
        self.boundaries      = []



    # Note::read_i2b2()
    #
    # @param txt. A file path for the i2b2 tokenized medical record
    # @param con. A file path for the i2b2 annotated concepts associated with txt
    def read_i2b2(self, txt, con=None):

        # Read in the medical text
        with open(txt) as f:
            for line in f:
                # Add sentence to the data list
                self.data.append(line.split())

                # Make put a temporary 'O' in each spot
                self.boundaries.append( ['O' for _ in line.split()] )


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

                    # Beginning of a concept
                    try:
                        self.boundaries[l-1][start] = 'B'
                    except:
                        print 'txt: ', txt
                        print 'con: ', con

                    # Inside of a concept
                    for i in range(start,end):
                        self.boundaries[l-1][i+1] = 'I'

                    #print "\n" + "-" * 80

            # Concept file does not guarantee ordering by line number
            self.classifications = sorted(classifications, key=lambda t:t[1])



    def write_txt(self):

        """
        Note::write_txt()

        Purpose: Output the text of a file (without xml annotations)

        @return  A string containing the text of the file.
        """

        retStr = ''

        for line in self.txtlist():
            retStr += ' '.join(line) + '\n'

        return retStr



    def write_i2b2_con(self, labels=None):

        """
        Note::write_i2b2_con()
        
        Purpose: Return the given concept label predictions in i2b2 format
        
        @param  labels. A list of classifications
        @return         A string of i2b2-concept-file-formatted data
        """

        # Return value
        retStr = ''

        # List of list of words (line-by-line)
        tlist = self.txtlist()


        # If given labels to write, use them. Default to self.classifications
        if labels:
            classifications = labels
        elif self.classifications:
            classifications = self.classifications
        else:
            raise Exception('Cannot write concept file: must specify labels')


        # For each classification
        for classification in classifications:

            # Ensure 'none' classifications are skipped
            if classification[0] == 'none':
                raise('Classification label "none" should never happen')

            concept = classification[0]
            lineno  = classification[1] + 1
            start   = classification[2]
            end     = classification[3]

            # A list of words (corresponding line from the text file)
            text = tlist[lineno-1]

            #print "\n" + "-" * 80
            #print "start:       ", start
            #print "end          ", end
            #print "text:        ", text
            #print "text[start]: ", text[start]
            #print "concept:     ", concept

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




    def write_BIOs_labels(self, filename, labels):

        """
        Note::write_BIOs_labels()
        
        Purpose: Print the prediction of BIOs concept boundary classification
        
        @param  _.      Filename. Ignore it.
        @param  labels. A list of list of BIOs labels
        """

        fid = open(filename,"w")

        # List of list of words (line-by-line)
        text = self.txtlist()

        for i, concept_line in enumerate(labels):
    
            # stores the current streak
            queue = [] 

            # C-style array indexing. Probably could be done a better way.
            # Used because I needed the ability of lookahead
            for j in range(len(concept_line)):
    
                # Beginning of a concept boundary
                if concept_line[j] != 'O':
    
                    # Increase size of current streak
                    queue.append(text[i][j])
    
                    # lookahead (check if streak will continue)
                    if (j+1 == len(concept_line))or \
                       (concept_line[j+1] != 'I'):
                           print >>fid, '%d:%d %d:%d' % (i+1,j-len(queue)+1,i+1,j)
                           print >>fid, ' '.join(queue)
                           print >>fid, ''
                           # Reset streak
                           queue = []
        


    # Note::read_plain()
    #
    # @param txt. A file path for the plain tokenized medical record
    # @param con. A file path for the annotated concepts associated with txt
    def read_plain(self, txt, con=None):

        # Read in the medical text
        with open(txt) as f:

            for line in f:
                # Add sentence to the data list
                self.data.append(line)

                # For each word, store a corresponding concept label
                tmp = []
                for word in line.split():
                    tmp.append('none')
                self.concepts.append(tmp)


        # If an accompanying concept file was specified, read it
        if con:
            with open(con) as f:
                for line in f:
                    c, t = line.split('||')
                    t = t[3:-2]
                    c = c.split()

                    start = c[-2].split(':')
                    end = c[-1].split(':')

                    assert "concept spans one line", start[0] == end[0]
                    l = int(start[0]) - 1
                    start = int(start[1])
                    end = int(end[1])

                    # Tokenize the input intervals
                    stok = len(self.data[l][:start].split())
                    etok = len(self.data[l][start:end+1].split()) + stok - 1

                    # Update the corresponding concept labels
                    for i in range(stok, etok + 1):
                        self.concepts[l][i] = t



    # Note::write_plain()
    #
    # @param  con.    A path to the file of where to write the prediction.
    # @param  labels. A list of predictions of labels for the given text.
    #
    # Write the concept predictions to a given file in plain format
    def write_plain(self, con, labels):

        with open(con, 'w') as f:

            # Search every token
            for i, line in enumerate(labels):
                for j, label in enumerate(line):

                    # Only print non-trivial tokens
                    if label != 'none':
                        
                        words = self.data[i].split()

                        # Get the untokenized starting index
                        start = 0
                        for k in range(j):
                            start += len(words[k]) + 1

                        # Untokenized ending index
                        end = start + len(words[j]) - 1

                        # Format the starting and ending indices
                        sidx = "%d:%d" % (i + 1, start)
                        eidx = "%d:%d" % (i + 1, end)

                        # Get the string stored in the plaintext representation
                        datum = self.data[i][start:end+1]

                        print >>f, "c=\"%s\" %s %s||t=\"%s\"" % (datum, sidx, eidx, label)



    def read_xml(self, xml):

        """
        Note::read_xml()
        
        Purpose: Read data from an xml-annotated file into a Note object

        @param xml. A file path for the xml formatted medical record
        """

        # Read in the medical text
        with open(xml) as f:

            for lineno,line in enumerate(f.readlines()):

                # Add sentence to the data list
                data_line = []
                for word in line.split():
                    if (word[0] != '<') and (word[-1] != '>'):
                        data_line.append(word)
                self.data.append(data_line)


                # Stored data for self.classifications
                concept = 'N/A'
                start_ind = -1
                i = 0

                # State variable is sufficient because concepts are not nested
                inside_concept = False
                for word in line.split():

                    # Search for xml tag
                    match = re.search('<(.*)>', word)
                    if match:

                        con = match.group(1)
                        
                        # end tag
                        if con[0] != '/':
                            # store data 
                            concept = con
                            start_ind = i

                            # state variable
                            inside_concept = True

                        # begin tag
                        else:
                            # store data 
                            tup = (concept,lineno,start_ind,i-1)
                            self.classifications.append(tup)

                            # state variable
                            inside_concept = False

                    # non-tag text
                    else:

                        # Next token
                        i += 1


    def write_xml(self, labels=None):

        """
        Note::write_xml()
        
        Purpose: Write the concept predictions in xml format
        
        @param  labels. A list of predictions of labels for the given text.
        @return         A string for the xml-annotated file
        """


        # If given labels to write, use them. Default to self.classifications
        if labels:
            classifications = labels
        elif self.classifications:
            classifications = self.classifications
        else:
            raise Exception('Cannot write concept file: must specify labels')


        # Intermediate copy
        toks = copy(self.data)

        # Order classification tuples so they are accessed right to left
        # Assumption: sorted() is a stable sort
        tags = sorted(classifications, key=lambda x:x[2], reverse=True)
        tags = sorted(tags           , key=lambda x:x[1]              )

        #print toks
        #print ''
        #print ''

        # Insert each xml tag into its proper location
        for tag in tags:

            # Decode classification tuple
            con   = tag[0]
            line  = tag[1] - 1
            start = tag[2]
            end   = tag[3]

            #print tag
            #print 'line:   ', toks[line]
            #print 'phrase: ', toks[line][start:end+1]

            # Insert tags
            toks[line].insert(end+1, '</' + con + '>')
            toks[line].insert(start, '<'  + con + '>')

            #print 'line:   ', toks[line]
            #print ''


        # Stitch text back together
        toks = [  ' '.join(s)  for  s  in toks  ]
        toks = '\n'.join(toks)

        #print toks
        #print ''
        #print ''


        return toks




    # txtlist()
    #
    # @return the data from the medical text broken into line-word format
    def txtlist(self):
        return self.data



    def conlist(self):
        """
        Useful during evaluation
        """

        # Cached for later calls
        if self.concepts: return self.concepts


        # For each word, store a corresponding concept label
        # Initially, all labels will be stored as 'none'
        for line in self.data:
            tmp = []
            for word in line:
                tmp.append('none')
            self.concepts.append(tmp)


       # Use the classifications to correct all mislabled 'none's
        for classification in self.classifications:

            #print "classification:    ", classification
            #print "classification[0]: ", classification[0]
            #print "classification[1]: ", classification[1]
            #print "classification[2]: ", classification[2]
            #print "classification[3]: ", classification[3]

            concept = classification[0]
            lineno  = classification[1] - 1
            start   = classification[2]
            end     = classification[3]            

            self.concepts[lineno][start] = concept
            for i in range(start, end):
                self.concepts[lineno][i+1] = concept

        return self.concepts



    def concept_labels(self):

        """
        concept_labels()

        Purpose: Training labels for a concept classifier on phrases

        @ return A list of concept labels (1:1 mapping with text_chunks() output)
        """

        return [  c[0]  for  c  in  self.classifications  ]



    def iob_labels(self):
        """
        return a list of list of IOB labels
        """
        return self.boundaries



    def set_iob_labels(self, iobs):
        """
        return a list of list of IOB labels
        """

        # Must be proper form
        for iob in iobs:
            for label in iob:
                assert (label == 'O') or (label == 'B') or (label == 'I'),  \
                       "All labels must be I, O, or B. Given: " + label

        self.boundaries = iobs



    def chunked_text(self):

        """
        Note::generate_chunks()

        Purpose: Combine all 'I's into 'B' chunks

        @return A list of list of phrases.
        """


        # List of list of phrases
        text          = self.txtlist()
        text_chunks   = []


        # Line-by-line chunking
        for sent,iobs in zip(self.txtlist(),self.iob_labels()):

            # One line of chunked phrases
            line = []

            # Chunk phrase (or single word if 'O' iob tag)
            phrase = ''

            # Word-by-word grouping
            for word,iob in zip(sent,iobs):

                if iob == 'O':
                    if phrase: line.append(phrase)
                    phrase = word

                if iob == 'B':
                    if phrase: line.append(phrase)
                    phrase = word

                if iob == 'I':
                    phrase += ' ' + word

            # Add last phrase
            if phrase: line.append(phrase)
            
            # Add line from file 
            text_chunks.append(line)


        return text_chunks




    def concept_indices(self):

        # Return value
        inds_list = []


        # Line-by-line chunking
        for iobs in self.iob_labels():

            # One line of chunked phrases
            line = []
            seen_chunks = 0

            # Word-by-word grouping
            for iob in iobs:

                if iob == 'O':
                    seen_chunks += 1

                if iob == 'B':
                    line.append(seen_chunks)
                    seen_chunks += 1

            # Add line from file
            inds_list.append(line)


        return inds_list



