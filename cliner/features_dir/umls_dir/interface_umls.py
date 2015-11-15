#
# Interface to UMLS Databases and concept trie
#
#
#


import copy
import sqlite3
import create_sqliteDB
import os
import sys

import create_trie


features_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if features_dir not in sys.path:
    sys.path.append(features_dir)


# find where umls tables are located
from read_config import enabled_modules
enabled = enabled_modules()
umls_tables = enabled['UMLS']




############################################
###          Setups / Handshakes         ###
############################################


#connect to UMLS database
def SQLConnect():
    #try to connect to the sqlite database.
    # if database does not exit. Make one.
    db_path = os.path.join(umls_tables, "umls.db")
    if not os.path.isfile(db_path):
        print "\n\tdb doesn't exist (creating one now)\n"
        create_sqliteDB.create_db()

    db = sqlite3.connect( db_path )
    return db.cursor()




############################################
###      Global reource connections      ###
############################################


# Global database connection
c = SQLConnect()

# Global trie
trie = create_trie.create_trie()




############################################
###           Query Operations           ###
############################################


def string_lookup( string ):
    """ Get sty for a given string """
    try:
        c.execute( "SELECT sty FROM MRCON a, MRSTY b WHERE a.cui = b.cui AND str = ?; " , (string,) )
        return c.fetchall()
    except sqlite3.ProgrammingError, e:
        return []


def cui_lookup( string ):
    """ get cui for a given string """
    try:
        # Get cuis
        c.execute( "SELECT cui FROM MRCON WHERE str = ?;" , (string,) )
        return c.fetchall()
    except sqlite3.ProgrammingError, e:
        return []


def concept_exists(string):
    """ Fast query for set membership in trie """
    return unicode(string) in trie


if __name__ == "__main__":

 #   print string_lookup("blood")
#    print cui_lookup("blood")
#    print concept_exists("blood")
    pass




