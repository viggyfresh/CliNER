import copy 
import sqlite3
import create_sqliteDB
import os 

WINDOW_SIZE = 7 

#connect to UMLS database 
def SQLConnect():

    #try to connect to the sqlite database. Make one otherwise
    if( os.path.isfile( "../umls_tables/umls.db" ) ):
        print "\ndb exists" 
        db = sqlite3.connect( "../umls_tables/umls.db" ) 
    else:
        print "\ndb doesn't exist"
        create_sqliteDB.create_db() 
        db = sqlite3.connect( "../umls_tables/umls.db" )
    db.text_factory = str
    return db.cursor()

#used in SQlookup, I made this global so SQLConnect is only called once. 
c = SQLConnect()

#searchs umls database for the semantic type of a string 
def SQlookup( c , string ):

    #queries database and finds first semantic type match, returns a 1 when a match is found. 
    c.execute( "SELECT sty FROM MRCON a, MRSTY b WHERE a.cui = b.cui AND str = ? LIMIT 1;" , (string,) )

    #returns a tuple with the match or None if there was  no match.  
    return c.fetchone() 

#returns the semantic type of a word 
def string_lookup( string ):
    
    return SQlookup( c ,  string )

