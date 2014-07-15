from __future__ import with_statement

import re


class Note:

    # Constructor
    def __init__(self):
        # data     - A list of lines directly from the file
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
                self.data.append(line)

                # Make put a temporary 'O' in each spot
                self.boundaries.append( ['O' for _ in line.split()] )


        # If an accompanying concept file was specified, read it
        if con:
            with open(con) as f:
                for line in f:

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
                    self.classifications.append( (conc,l,start,end) )

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



    # Note::write_i2b2()
    #
    # @param  con.    A path to the file of where to write the prediction.
    # @param  labels. A list of classifications
    #
    # Write the concept predictions to a given file in i2b2 format
    def write_i2b2(self, con, labels):

        # List of list of words (line-by-line)
        tlist = self.txtlist()

        #for i, elem in enumerate(self.data):
        #    print i, ": ", elem


        with open(con, 'w') as f:

            for classification in labels:

                    # Ensure 'none' classifications are skipped
                    if classification[0] == 'none':
                        continue

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
                    print >>f, "c=\"%s\" %s %s||t=\"%s\"" % (datum, idx1, idx2, label)
                    #print "c=\"%s\" %s %s||t=\"%s\"" % (datum, idx1, idx2, label)



    # Note::write_BIOs_labels()
    #
    # @param  _.      Filename. Ignore it.
    # @param  labels. A list of list of BIOs labels
    #
    # Print the prediction of BIOs concept boundary classification
    def write_BIOs_labels(self, filename, labels):

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



    # Note::read_xml()
    #
    # @param txt. A file path for the xml formatted medical record
    def read_xml(self, txt):

       # FIXME: By storing the 'data' as a list of lines from the file
       #          instead of a list of list of words, xml does not fit nicely
       # Possible solution: Switch back to list of list of words
       # Alternative:       Store edited sentences from the file to remove <>


        # Read in the medical text
        with open(txt) as f:

            for line in f:
                # Add sentence to the data list
                self.data.append(line)


                # For each word, store a corresponding concept label
                tmp = []
                for i, group in enumerate(line.split('<')):
                    # All odd groups have label info (because of line split)
                    # ex. 'treatment>discharge medications'
                    if (i%2):
                        # Get concept label
                        match = re.search('(\w+)>(.+)', group)
                        if not match: 
                            print "\nUnexpected file format\n"
                            exit(1)

                        label = match.group(1)
                        words = match.group(2)
                       
                        # Add the label once for every word
                        for word in words.split():
                            tmp.append(label)
                    # If even group , then process with 'none' labels
                    else:
                        for word in group.split():
                # / closes the xml tag of a previous label (skip)
                            if word[0] == '/':
                                continue
                            else:
                                tmp.append('none')
                # Add line of labels to the 'concepts' data member
                self.concepts.append(tmp)



    # Note::write_xml()
    #
    # @param  con.    A path to the file of where to write the prediction.
    # @param  labels. A list of predictions of labels for the given text.
    #
    # Write the concept predictions to a given file in xml format
    def write_xml(self, con, labels):
        # xml formats do not have associated concept files
        return




    # txtlist()
    #
    # @return the data from the medical text broken into line-word format
    def txtlist( self ):
        # Goal: Break self.data sentences into lists of words
        ans = []
        for sent in self.data:
            ans.append(sent.split())

        return ans



    def concept_labels(self):

        """
        concept_labels()

        Purpose: Training labels for a concept classifier on phrases

        @ return A list of concept labels (1:1 mapping with text_chunks() output)
        """

        return [  c[0]  for  c  in  self.classifications  ]



    # boundaries()
    #
    # @return a list of lists of the BIO vals associated with each word from data
    def iob_labels( self ):
        return self.boundaries



    def text_chunks(self):

        """
        Note::generate_chunks()

        Purpose: A list of non-'none' labeled phrases 

        @return A list of phrases.
        """

        retVal = []

        # Get phrase from each classification tuple (AKA each non-'none' concept)
        for c in self.classifications:

            # Extract data
            lineno = c[1] - 1
            start  = c[2]
            end    = c[3]

            # Add phrase to list
            line = self.data[lineno].split()
            phrase_list = line[start:end+1]
            phrase = ' '.join(phrase_list)
            retVal.append( phrase )


        return retVal
