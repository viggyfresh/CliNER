

if __name__ == '__main__':
    import doctest
    
    import os, sys
    home = os.path.join( os.getenv('CLINER_DIR') , 'cliner' )
    if home not in sys.path: sys.path.append(home)
    import features_dir.utilities
    doctest.testmod(features_dir.utilities)
