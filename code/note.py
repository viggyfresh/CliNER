"""Internal note representation.

Note class reads in i2b2 formatted .txt and .con files and aligns them. After-
ward they can be accessed by iterating over the class.

Three auxiliary methods, read_txt(), read_con(), and write_con() streamline 
help manipulate such files as well.
"""
# TODO: clean up interface
# TODO: add support for non-i2b2 formats

from __future__ import with_statement


# This is a test

class Note:
	"""Note representation.

	Notes are represented as an iterable of tuples (word, concept).
	"""
	# TODO: more efficient internal representation

	def __init__(self, txt, con=None):
		"""Read in the note from file(s).

		Args:
			txt: File containing i2b2-formatted text.
			con: File containing i2b2-formatted concepts.
		"""

		# Read in list of tokens, each with "none" concept
		self.sents = []
		with open(txt) as f:
			for line in f:
				self.sents.append([[w, "none"] for w in line.split()])
		
		# Assign appropriate concept if a concept file was given
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
						self.sents[l][i][1] = t

	def __iter__(self):
		"""Yield the (word, concept) pairs."""
		return iter(self.sents)
		
def read_txt(txt):
	"""Get a list of words from an i2b2-formatted text file.

	Ags:
		txt: The i2b2-formatted text file.

	Returns:
		A list of the words in the text file.
	"""
	# TODO: this method is misleading, should include concept for consistency

	note = []
	with open(txt) as f:
		for line in f:
			note.append([w for w in line.split()])
	return note		
	
def read_con(con, txt):
	"""Get a list of (word, concept) pairs from a txt and con file.

	Args:
		con: File containing the i2b2-formatted concepts.
		txt: File containing the i2b2-formatted text.

	Returns:
		A list of (word, concept) pairs.
	"""
	# TODO: this method obviates the Note class, should complement

	label = [['none'] * len(line) for line in txt]
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
				label[l][i] = t
	return label
		
def write_con(con, data, labels):
	"""Writes concept file.

	From data and labels, this create a .con file as output.
	"""
	# TODO: method should call a serialization primitive of Note class

	with open(con, 'w') as f:
		for i, tmp in enumerate(zip(data, labels)):
			datum, label = tmp
			for j, tmp in enumerate(zip(datum, label)):
				datum, label = tmp
				if label != 'none':
					idx = "%d:%d" % (i + 1, j)
					print >>f, "c=\"%s\" %s %s||t=\"%s\"" % (datum, idx, idx, label)
