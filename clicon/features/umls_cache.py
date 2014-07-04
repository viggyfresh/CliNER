import cPickle as pickle 
import os

class UmlsCache:
    def __init__(self):
        try:
            db_dir = os.path.join( os.environ['CLICON_DIR'], 'umls_tables' )
            filename = os.path.join( db_dir, 'umls_cache' )
            self.cache = pickle.load( open( filename , "rb" ) ) ;
        except IOError:
            self.cache = {} 
    
    def has_key( self , string ): 
        return self.cache.has_key( string )  

    def add_map( self , string, mapping ):
        self.cache[string] = mapping 

    def get_map( self , string ):
        return self.cache[string] 
 
    def __del__(self):  
        db_dir = os.path.join( os.environ['CLICON_DIR'], 'umls_tables' )
        filename = os.path.join( db_dir, 'umls_cache' )
        pickle.dump( self.cache, open(filename, "wb" ) )    
