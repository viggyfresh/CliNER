import copy 
import sqlite3
import create_sqliteDB
import os 

WINDOW_SIZE = 7 

#connect to UMLS database 
def SQLConnect():

    #try to connect to the sqlite database. Make one otherwise
    db_path = os.path.join( os.environ['CLICON_DIR'], "umls_tables/umls.db")
    if( os.path.isfile( db_path ) ):
        print "\ndb exists" 
    else:
        print "\ndb doesn't exist"
        create_sqliteDB.create_db() 

    db = sqlite3.connect( db_path )
    return db.cursor()


#used in SQlookup, I made this global so SQLConnect is only called once. 
c = SQLConnect()

#searchs umls database for the semantic type of a string 
def SQlookup( c , string ):

    #queries database and finds first semantic type match, returns a 1 when a match is found. 
    c.execute( "SELECT sty FROM MRCON a, MRSTY b WHERE a.cui = b.cui AND str = ?; " , (string,) )

    #returns a tuple with the match or None if there was  no match.  
    #return c.fetchone() 
    return c.fetchall() 

#returns the semantic type of a word 
def string_lookup( string ):
    
    #return SQlookup( c ,  string )
    r = SQlookup( c ,  string )

    return r


# get all semantic types for a given concept
def cui_lookup( string ):

    # queries database and finds semantic type match
    c.execute( "SELECT cui FROM MRCON WHERE str = ?;" , (string,) )

    #returns a tuple with the match or None if there was  no match.  
    return c.fetchall() 


def hypernyms_lookup( string ):

    c.execute( "SELECT CUI FROM MRCON WHERE STR = ? LIMIT 1 ;" , (string,) )

    cui = c.fetchone()

    if cui == None:
        return None
    else:
        c.execute( "SELECT CUI2 FROM MRREL WHERE CUI1 = ? AND REL = 'PAR' LIMIT 5 ;" , (cui[0],) )
        result = c.fetchone()
        if not result:
            return None
        else:
            return result


