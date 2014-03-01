#database.py creates a .db file for performing umls searches. 
import sqlite3  
import sys

def create_db(): 
    
    print "\ncreating umls.db" 
    #connect to the .db file we are creating. 
    conn = sqlite3.connect( "../umls_tables/umls.db" ) 
    
    conn.text_factory = str 

    #load data in files.
    try:
        MRSTY_TABLE = open( ( "../umls_tables/MRSTY"), "r" )
    except IOError:
        print "\nNo file to use for creating MRSTY table\n" 
        conn.close() 
        sys.exit() 

    try:
        MRCON_TABLE = open( ("../umls_tables/MRCON") , "r" ) 
    except IOError:
        print "\nNo file to use for creating MRCON table\n" 
        conn.close() 
        sys.exit() 

    MRSTY_TABLE = MRSTY_TABLE.read() ;
    MRSTY_TABLE = MRSTY_TABLE.split('\n')

    MRCON_TABLE = MRCON_TABLE.read() ; 
    MRCON_TABLE = MRCON_TABLE.split( '\n' ) 

    #data that will be inserted into tables. 
    MRTSY_DATA = [] 
    MRCON_DATA = [] 

    c = conn.cursor() 

    #parse and store the data from the files. 
    for line in MRSTY_TABLE: 
        MRTSY_DATA.append( tuple(line.split('|')) )
    for line in MRCON_TABLE:
        MRCON_DATA.append( tuple(line.split('|')) )

    #create tables. 
    c.execute( "CREATE TABLE MRCON( CUI, LAT, TS, LUI, STT, SUI, STR, LRL, EMPTY ) ;" )
    c.execute( "CREATE TABLE MRSTY( CUI, TUI, STY, EMPTY ) ;" )  

    #insert data onto database
    for line in MRCON_DATA:
        try:
            c.execute( "INSERT INTO MRCON( CUI, LAT, TS, LUI, STT, SUI, STR, LRL, EMPTY ) values ( ?, ?, ? ,?, ?,?,?,?,?);", line )
        except sqlite3.ProgrammingError:
            continue
    for line in MRTSY_DATA:
        try:
            c.execute( "INSERT INTO MRSTY( CUI, TUI, STY, EMPTY) values( ?, ?, ?, ?)" , line )  
        except sqlite3.ProgrammingError:
            continue 

    #create indices for faster queries
    c.execute( "CREATE INDEX mrsty_cui_map ON MRSTY(CUI)")  
    c.execute( "CREATE INDEX mrcon_str_map ON MRCON(STR)")  
    c.execute( "CREATE INDEX mrcon_cui_map ON MRCON(CUI)")

    #save changes to .db
    conn.commit()

    print "\nsqlite database created" 

    #close connection
    conn.close()

