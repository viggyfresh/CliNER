from __future__ import with_statement

import os
import cPickle as pickle
import helper
import sci
import sys

from sklearn.feature_extraction  import DictVectorizer
from features import clicon_features


class Model:
    
    labels = {
        "none":0,
        "treatment":1,
        "problem":2,
        "test":3
    }
    reverse_labels = {v:k for k, v in labels.items()}
    

    # IOBs labels
    IOBs_labels = {
        'O':0,
        'B':1,
        'I':2
    }
    reverse_IOBs_labels = {v:k for k,v in IOBs_labels.items()}


    @staticmethod
    def load(filename='awesome.model'):
        with open(filename, 'rb') as model:
            model = pickle.load(model)
        model.filename = filename
        return model


    def __init__(self, filename='awesome.model', type=sci.LIN):

        model_directory = os.path.dirname(filename)
        if model_directory != "":
            helper.mkpath(model_directory)

        self.filename = os.path.realpath(filename)

        # DictVectorizers
        self.first_prose_vec    = DictVectorizer()
        self.first_nonprose_vec = DictVectorizer()
        self.second_vec         = DictVectorizer()

        # Classifiers
        self.first_prose_clfs    = {}
        self.first_nonprose_clfs = {}
        self.second_clfs         = {}

        # FIXME: Only using scikit's SVM
        self.type = sci.LIN
        


    def train(self, notes):

        """
        Model::train()

        Purpose: Train a ML model on annotated data

        @param notes. A list of Note objects (containing text and annotations)
        @return       None
        """


        ##############
        # First pass #
        ##############

        # Get the data and annotations from the Note objects
        text    = [  note.txtlist()        for  note  in  notes  ]
        ioblist = [  note.iob_labels()     for  note  in  notes  ]

        data1 = reduce( concat,    text )
        Y1    = reduce( concat, ioblist )


        # Train classifier (side effect - saved as object's member variable)
        print '\tfirst pass'
        self.first_train(data1, Y1, do_grid=False)



        ###############
        # Second pass #
        ###############

        # Get the data and annotations from the Note objects
        chunks  = [  note.chunked_text()    for  note  in  notes  ] 
        indices = [  note.concept_indices() for  note  in  notes  ]
        conlist = [  note.concept_labels()  for  note  in  notes  ]

        data2 = reduce( concat, chunks  )
        inds  = reduce( concat, indices )
        Y2    = reduce( concat, conlist )


        # Train classifier (side effect - saved as object's member variable)
        print '\tsecond pass'
        self.second_train(data2, inds, Y2, do_grid=False)



        # Pickle dump
        print '\tpickle dump'
        with open(self.filename, "wb") as model:
            pickle.dump(self, model)
    



    def first_train(self, data, Y, do_grid=True):

        """
        Model::first_train()

        Purpose: Train the first pass classifiers (for IOB chunking)

        @param data      A list of split sentences    (1 sent = 1 line from file)
        @param Y         A list of list of IOB labels (1:1 mapping with data)
        @param feat_obj  A wrapper for the feature module
        @param do_grid   A boolean indicating whether to perform a grid search

        @return          None
        """

        # Create object that is a wrapper for the features
        feat_obj = clicon_features.FeatureWrapper(data)

        print '\t\textracting features (pass one)'

        # IOB tagging
        # FIXME - Partition and then batch features
        prose    = []
        nonprose = []
        prose_line_numbers    = []
        nonprose_line_numbers = []
        for i,line in enumerate(data):
            isProse,feats = feat_obj.IOB_features(line)
            if isProse:
                prose += feats 
                prose_line_numbers.append(i)
            else:
                nonprose += feats 
                nonprose_line_numbers.append(i)


        # FIXME - very unclear what this is
        # Description: Separate labels by same division as text
        prose_ind    = 0
        nonprose_ind = 0
        pchunks = []
        nchunks = []
        p_end_flag = False
        n_end_flag = False
        for i,line in enumerate(Y):
            if   (not p_end_flag) and (i == prose_line_numbers[prose_ind]):
                pchunks += line
                prose_ind += 1
                if prose_ind == len(prose_line_numbers): p_end_flag = True
            elif (not n_end_flag) and (i == nonprose_line_numbers[nonprose_ind]):
                nchunks += line
                nonprose_ind += 1
                if nonprose_ind == len(nonprose_line_numbers): n_end_flag = True
            else:
                # Should never really get here
                print 'Line #%d is neither prose nor nonprose!' % i
                print line, '\n'


        print '\t\tvectorizing features (pass one)'


        # Vectorize IOB labels
        Y_prose    = [  Model.IOBs_labels[y]  for  y  in  pchunks  ]
        Y_nonprose = [  Model.IOBs_labels[y]  for  y  in  nchunks  ]


        # Vectorize features
        X_prose    =    self.first_prose_vec.fit_transform(   prose)
        X_nonprose = self.first_nonprose_vec.fit_transform(nonprose)


        print '\t\ttraining classifier (pass one)'


        # Train classifiers
        self.first_prose_clfs    = sci.train(X_prose   , Y_prose   , self.type, do_grid)
        self.first_nonprose_clfs = sci.train(X_nonprose, Y_nonprose, self.type, do_grid)



    # Model::second_train()
    #
    #
    def second_train(self, data, inds_list, Y, do_grid=True):

        """
        Model::second_train()

        Purpose: Train the first pass classifiers (for IOB chunking)

        @param data      A list of list of strings.
                           - A string is a chunked phrase
                           - An inner list corresponds to one line from the file
        @param inds_list A list of list of integer indices
                           - assertion: len(data) == len(inds_list)
                           - one line of 'inds_list' contains a list of indices
                               into the corresponding line for 'data'
        @param Y         A list of concept labels
                           - assertion: there are sum(len(inds_list)) labels
                              AKA each index from inds_list maps to a label
        @param do_grid   A boolean indicating whether to perform a grid search

        @return          None
        """


        # Create object that is a wrapper for the features
        feat_o = clicon_features.FeatureWrapper()


        print '\t\textracting features (pass two)'


        # Extract features
        X = [ feat_o.concept_features(s,inds) for s,inds in zip(data,inds_list) ]
        X = reduce(concat, X)


        print '\t\tvectorizing features (pass two)'


        # Vectorize labels
        Y = [  Model.labels[y]  for  y  in  Y  ]

        # Vectorize features
        X = self.second_vec.fit_transform(X)


        print '\t\ttraining classifier (pass two)'


        # Train the model
        self.second_clfs = sci.train(X, Y, self.type, do_grid)



        
    # Model::predict()
    #
    # @param note. A Note object that contains the data
    def predict(self, note):


        ##############
        # First pass #
        ##############


        print '\tfirst pass'


        # Get the data and annotations from the Note objects
        data   = note.txtlist()

        # Predict IOB labels
        iobs = self.first_predict(data)
        note.set_iob_labels(iobs)



        ###############
        # Second pass #
        ###############


        print '\tsecond pass'


        # Get the data and annotations from the Note objects
        chunks = note.chunked_text()
        inds   = note.concept_indices()

        # Predict concept labels
        retVal = self.second_predict(chunks,inds)


        return retVal




    # Model::first_predit()
    #
    # @param data. A list of list of words
    # @return      A list of list of IOB tags
    def first_predict(self, data):

        # Create object that is a wrapper for the features
        feat_obj = clicon_features.FeatureWrapper(data)
 

        print '\t\textract features (pass one)'


        # FIXME - partition and batch
        # prose and nonprose - each store a list of sentence feature dicts
        prose    = []
        nonprose = []
        prose_line_numbers    = []
        nonprose_line_numbers = []
        for i,line in enumerate(data):
            # returns both the feature dict AND whether the sentence was prose
            isProse,feats = feat_obj.IOB_features(line)
            if isProse:
                prose    += feats 
                prose_line_numbers.append(i)
            else:
                nonprose += feats 
                nonprose_line_numbers.append(i)


        print '\t\tvectorize features (pass one)'


        # Vectorize features
        X_prose    =    self.first_prose_vec.transform(   prose)
        X_nonprose = self.first_nonprose_vec.transform(nonprose)


        print '\t\tpredict labels (pass one)'


        # Predict
        out_p = sci.predict(self.first_prose_clfs   , X_prose,   sci.LIN)
        out_n = sci.predict(self.first_nonprose_clfs, X_nonprose,sci.LIN)


        # Format labels
        plist = [  n  for  n  in  list(out_p[sci.LIN]) ]
        nlist = [  n  for  n  in  list(out_n[sci.LIN]) ]
        

        # Stitch prose and nonprose labels lists together
        labels = []
        prose_ind    = 0
        nonprose_ind = 0
        p_end_flag = (len(   prose_line_numbers) == 0)
        n_end_flag = (len(nonprose_line_numbers) == 0)


        for i in range( len(data) ):
            if   (not p_end_flag) and (i == prose_line_numbers[prose_ind]):
                line  = plist[0:len(data[i]) ] # Beginning
                plist = plist[  len(data[i]):] # The rest
                labels += line
                prose_ind += 1
                if prose_ind == len(prose_line_numbers): p_end_flag = True

            elif (not n_end_flag) and (i == nonprose_line_numbers[nonprose_ind]):
                line  = nlist[0:len(data[i]) ] # Beginning
                nlist = nlist[  len(data[i]):] # The rest
                labels += line
                nonprose_ind += 1
                if nonprose_ind == len(nonprose_line_numbers): n_end_flag = True

            else:
                # Shouldn't really get here ever
                print 'Line #%d is neither prose nor nonprose!' % i



        # translate IOB labels into a readable format
        # ex. change all occurences of 1 -> 'B'
        iobs = []
        for sentence in data:
            iobs.append([labels.pop(0) for i in range(len(sentence))])
            iobs[-1]= map(lambda l: Model.reverse_IOBs_labels[int(l)],iobs[-1])


        # list of list of IOB labels
        return iobs




    def second_predict(self, data, inds_list):

        # Create object that is a wrapper for the features
        feat_o = clicon_features.FeatureWrapper()


        print '\t\textract features (pass two)'


        # Extract features
        X = [ feat_o.concept_features(s,inds) for s,inds in zip(data,inds_list) ]
        X = reduce(concat, X)


        print '\t\tvectorize features (pass two)'


        # Vectorize features
        X = self.second_vec.transform(X)


        print '\t\tpredict labels (pass two)'


        # Predict concept labels
        out = sci.predict(self.second_clfs, X, sci.LIN)



        # FIXME - Output prediction labels are entirely wrong
        # ex. trained on file with 3 concepts (prob,treat,treat) and predicted
        #        on same file. Got (test,test,test) as labels

        retVal = {}
        for t in sci.bits(self.type):

            # Index into output dictionary
            o = list(out[t])
            classifications = []


            # Line-by-line processing
            for lineno,inds in enumerate(inds_list):

                # Skip empty line
                if not inds: continue


                # For each concept
                for ind in inds:

                    # Get next concept
                    concept = Model.reverse_labels[o.pop(0)]

                    # Get start position (ex. 7th word of line)
                    start = 0
                    for i in range(ind):
                        start += len( data[lineno][i].split() )

                    # Length of chunk
                    length = len(data[lineno][ind].split())

                    # Classification token
                    classifications.append(  (concept, lineno, start, start+length-1 ) )
            
                retVal[t] = classifications


        # Return values
        return retVal






def concat(a,b):
    """
    list concatenation function (for reduce() purpose)
    """
    return a+b
