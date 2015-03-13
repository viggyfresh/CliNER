#database.py creates a .db file for performing umls searches.
import sqlite3
import os
import sys
import os

def create_db():

    print "\ncreating umls.db"
    #connect to the .db file we are creating.
    db_path = os.path.join(os.environ['CLINER_DIR'],'umls_tables/umls.db')
    conn = sqlite3.connect( db_path )
    conn.text_factory = str

    print "opening files"
    #load data in files.
    try:
        mrsty_path = os.path.join(os.environ['CLINER_DIR'],'umls_tables/MRSTY')
        MRSTY_TABLE_FILE = open( mrsty_path, "r" )
    except IOError:
        print "\nNo file to use for creating MRSTY table\n"
        conn.close()
        sys.exit()

    try:
        mrcon_path = os.path.join(os.environ['CLINER_DIR'],'umls_tables/MRCON')
        MRCON_TABLE_FILE = open( mrcon_path , "r" )
    except IOError:
        print "\nNo file to use for creating MRCON table\n"
        conn.close()
        sys.exit()

    try:
        mrrel_path = os.path.join(os.environ['CLINER_DIR'],'umls_tables/MRREL')
        MRREL_TABLE_FILE = open( mrrel_path , "r" )
    except IOError:
        print "\nNo file to use for creating MRREL table\n"
        conn.close()
        sys.exit()

    print "creating tables"
    c = conn.cursor()

    #create tables.
    c.execute( "CREATE TABLE MRCON( CUI, LAT, TS, LUI, STT, SUI, STR, LRL, EMPTY ) ;" )
    c.execute( "CREATE TABLE MRSTY( CUI, TUI, STY, EMPTY ) ;" )
    c.execute( "CREATE TABLE MRREL( CUI1, REL, CUI2, RELA, SAB, SL, MG, EMPTY ) ;" )

    print "inserting data into MRSTY table"
    for line in MRSTY_TABLE_FILE:

        try:
            c.execute( "INSERT INTO MRCON( CUI, LAT, TS, LUI, STT, SUI, STR, LRL, EMPTY ) values ( ?, ?, ? ,?, ?,?,?,?,?);", tuple(line[0:-1].split('|')) )
        except sqlite3.ProgrammingError:
            continue

    MRSTY_TABLE_FILE.close()

    print "inserting data into MRCON table"
    for line in MRCON_TABLE_FILE:

        try:
            c.execute( "INSERT INTO MRSTY( CUI, TUI, STY, EMPTY) values( ?, ?, ?, ?)" , tuple(line[0:-1].split('|')) )
        except sqlite3.ProgrammingError:
            continue
    
    MRCON_TABLE_FILE.close()

    print "inserting data into MRREL table"
    for line in MRREL_TABLE_FILE:
        
        try:
            c.execute( "INSERT INTO MRREL(  CUI1, REL, CUI2, RELA, SAB, SL, MG, EMPTY ) values( ?, ?, ?, ?,?, ? ,? ,? )" , tuple(line[0:-1].split('|')) )
        except sqlite3.ProgrammingError:
            continue

    MRREL_TABLE_FILE.close()

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

if __name__ == "__main__":
    create_db()

