import cPickle as pickle 

class UmlsCache:
    def __init__(self):
        try:
            self.cache = pickle.load( open( "umls_cache" , "rb" ) ) ;
        except IOError:
            self.cache = {} 
    
    def has_key( self , string ): 
        return self.cache.has_key( string )  

    def add_map( self , string, mapping ):
        self.cache[string] = mapping 

    def get_map( self , string ):
        return self.cache[string] 
 
    def __del__(self):  
        pickle.dump( self.cache, open("umls_cache", "wb" ) )    
