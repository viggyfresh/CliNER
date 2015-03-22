#database.py creates a .db file for performing umls searches.
import marisa_trie
import sys
import os

def create_trie():

    """
    create_trie()

    Purpose: Build a trie of concepts from MRREL

    @return  A trie object
    """

    # Is trie already built & pickled?
    prefix = os.environ['CLINER_DIR']
    filename = os.path.join( prefix, 'umls_tables/umls-concept.trie' )
    try:

        t = marisa_trie.Trie().load(filename)

        return t

    except IOError:
        pass


    print "\ncreating concept-trie"

    #load data in files.
    print "opening file"
    try:
        mrcon_path = os.path.join(os.environ['CLINER_DIR'],'umls_tables/MRCON')
        MRCON_TABLE = open( mrcon_path , "r" )
    except IOError:
        print "\nNo file to use for creating MRCON table\n"
        conn.close()
        sys.exit()

    print "inserting data into concept-trie"

    #insert data onto database
    print "inserting data"
    concepts = []
    for line in MRCON_TABLE:

	l = tuple(line[0:-1].split('|'))

        if len(l) < 6: continue

        concept = l[6]

        # Ignore non-ascii
        try:
            concept.decode('ascii')
        except:
            continue

        #print type(concept)
        concepts.append(concept)

    print "creating trie"
    t = marisa_trie.Trie(concepts)

    print "concept-trie created"

    # Pickle trie

    t.save(filename)

    return t


if __name__ == '__main__':
    t = create_trie()
