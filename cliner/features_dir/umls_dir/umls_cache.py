import cPickle as pickle
import sys
import os

sys.path.append((os.environ["CLINER_DIR"] + "/cliner/features_dir"))

from utilities import load_pickled_obj

class UmlsCache:
    def __init__(self):
        try:
            prefix = os.environ['CLINER_DIR']
            self.filename = os.path.join( prefix, 'umls_tables/umls_cache' )

            self.cache = load_pickled_obj(self.filename)

        except IOError:
            self.cache = {}

    def has_key( self , string ):
        return self.cache.has_key( string )

    def add_map( self , string, mapping ):
        self.cache[string] = mapping

    def get_map( self , string ):
        return self.cache[string]

    def __del__(self):
        pickle.dump( self.cache, open( self.filename, "wb" ) )
