from __future__ import with_statement

import re


class Note:

    # Constructor
    def __init__(self):
	# data     - A list of lines directly from the file
	# concepts - A one-to-one correspondence of each word's concept
        self.data     = []
        self.concepts = []



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

		    for i in range(start, end + 1):
			self.concepts[l][i] = t



    # Note::write_i2b2()
    #
    # @param  con.    A path to the file of where to write the prediction.
    # @param  labels. A list of predictions of labels for the given text.
    #
    # Write the concept predictions to a given file in i2b2 format
    def write_i2b2(self, con, labels):

	with open(con, 'w') as f:
	    for i, tmp in enumerate(zip(self.txtlist(), labels)):
		datum, label = tmp
		for j, tmp in enumerate(zip(datum, label)):
		    datum, label = tmp
		    if label != 'none':
			idx = "%d:%d" % (i + 1, j)
			print >>f, "c=\"%s\" %s %s||t=\"%s\"" % (datum, idx, idx, label)



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



    # conlist()
    #
    # @return a list of lists of the concepts associated with each word from data
    def conlist( self ):
	return self.concepts



    # For iterating
    def __iter__(self):
	return iter(self.data)
