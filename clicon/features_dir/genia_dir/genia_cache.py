import cPickle as pickle
import os

class GeniaCache:
    def __init__(self):
        try:
            prefix = os.path.dirname(__file__)
            self.filename = os.path.join( prefix, 'genia_cache' )
            self.cache = pickle.load( open( self.filename , "rb" ) ) ;
        except IOError:
            self.cache = {}

    def has_key(self, key):
        return self.cache.has_key( str(key) )

    def add_map(self, key, value):
        self.cache[ str(key) ] = value

    def get_map(self, key):
        return self.cache[ str(key) ]

    def __del__(self):
        pickle.dump( self.cache, open( self.filename, "wb" ) )

