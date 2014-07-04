#database.py creates a .db file for performing umls searches. 
import sqlite3  
import sys
import os

def create_db(): 
    
    print "\ncreating umls.db" 
    #connect to the .db file we are creating. 
    db_dir = os.path.join( os.environ['CLICON_DIR'], 'umls_tables' )
    conn = sqlite3.connect( os.path.join(db_dir, 'umls.db') ) 
    
    conn.text_factory = str 

    print "opening files" 
    #load data in files.
    try:
        MRSTY_TABLE = open( os.path.join(db_dir,'MRSTY'), "r" )
    except IOError:
        print "\nNo file to use for creating MRSTY table\n" 
        conn.close() 
        sys.exit() 

    try:
        MRCON_TABLE = open( os.path.join(db_dir,'MRCON') , "r" ) 
    except IOError:
        print "\nNo file to use for creating MRCON table\n" 
        conn.close() 
        sys.exit() 

    try:
        MRREL_TABLE = open( os.path.join(db_dir,'MRREL') , "r" )
    except IOError:
        print "\nNo file to use for creating MRREL table\n"
        conn.close()
        sys.exit()

    print "reading files"

    MRSTY_TABLE = MRSTY_TABLE.read() 
    MRSTY_TABLE = MRSTY_TABLE.split('\n')

    MRCON_TABLE = MRCON_TABLE.read()  
    MRCON_TABLE = MRCON_TABLE.split( '\n' ) 

    MRREL_TABLE = MRREL_TABLE.read() 
    MRREL_TABLE = MRREL_TABLE.split( '\n' ) 

    #data that will be inserted into tables. 
    MRTSY_DATA = [] 
    MRCON_DATA = [] 
    MRREL_DATA = [] 

    c = conn.cursor() 

    print "parsing files" 

    #parse and store the data from the files. 
    for line in MRSTY_TABLE: 
        MRTSY_DATA.append( tuple(line.split('|')) )
    for line in MRCON_TABLE:
        MRCON_DATA.append( tuple(line.split('|')) )
    for line in MRREL_TABLE:
        MRREL_DATA.append( tuple(line.split('|')) )

    print "creating tables" 

    #create tables. 
    c.execute( "CREATE TABLE MRCON( CUI, LAT, TS, LUI, STT, SUI, STR, LRL, EMPTY ) ;" )
    c.execute( "CREATE TABLE MRSTY( CUI, TUI, STY, EMPTY ) ;" )  
    c.execute( "CREATE TABLE MRREL( CUI1, REL, CUI2, RELA, SAB, SL, MG, EMPTY ) ;" ) 

    print "inserting data" 

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
    for line in MRREL_DATA:
        try:
            c.execute( "INSERT INTO MRREL(  CUI1, REL, CUI2, RELA, SAB, SL, MG, EMPTY ) values( ?, ?, ?, ?,?, ? ,? ,? )" , line )
        except sqlite3.ProgrammingError:
            continue 

    print "creating indices" 

    #create indices for faster queries
    c.execute( "CREATE INDEX mrsty_cui_map ON MRSTY(CUI)")  
    c.execute( "CREATE INDEX mrcon_str_map ON MRCON(STR)")  
    c.execute( "CREATE INDEX mrcon_cui_map ON MRCON(CUI)")
    c.execute( "CREATE INDEX mrrel_cui2_map ON MRREL( CUI2 )" )
    c.execute( "CREATE INDEX mrrel_cui1_map on MRREL( CUI1 ) " ) 
    c.execute( "CREATE INDEX mrrel_rel_map on MRREL( REL )" ) 

    #save changes to .db
    conn.commit()

    print "\nsqlite database created" 

    #close connection
    conn.close()

