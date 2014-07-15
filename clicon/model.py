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
        with open(filename) as model:
            model = pickle.load(model)
        model.filename = filename
        return model


    def __init__(self, filename='awesome.model', type=sci.ALL):

        model_directory = os.path.dirname(filename)
        if model_directory != "":
            helper.mkpath(model_directory)

        self.filename = os.path.realpath(filename)

        # DictVectorizers
        self.first_prose_vec    = DictVectorizer()
        self.first_nonprose_vec = DictVectorizer()
        self.second_vec         = DictVectorizer()

        # Classifiers
        self.second_clfs         = {}
        self.first_prose_clfs    = {}
        self.first_nonprose_clfs = {}

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
        print 'first'
        self.first_train(data1, Y1)



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
        print 'second'
        self.second_train(data2, inds, Y2)



        # Pickle dump
        print 'pickle dump'
        with open(self.filename, "w") as model:
            pickle.dump(self, model)
    



    def first_train(self, data, Y):

        """
        Model::first_train()

        Purpose: Train the first pass classifiers (for IOB chunking)

        @param data.     A list of split sentences    (1 sent = 1 line from file)
        @param Y.        A list of list of IOB labels (1:1 mapping with X)
        @param feat_obj  A wrapper for the feature module

        @return          None
        """

        print '\tbegin first_train()'


        # Create object that is a wrapper for the features
        feat_obj = clicon_features.FeatureWrapper(data)


        print '\tfeat_obj created'


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


        print '\tfeatures assigned'
        print '\tsegregate "chunks" list into prose and nonprose'


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


        # Vectorize IOB labels
        Y_prose    = [  Model.IOBs_labels[y]  for  y  in  pchunks  ]
        Y_nonprose = [  Model.IOBs_labels[y]  for  y  in  nchunks  ]


        # Vectorize features
        X_prose    =    self.first_prose_vec.fit_transform(   prose)
        X_nonprose = self.first_nonprose_vec.fit_transform(nonprose)


        # Train classifiers
        self.first_prose_clfs    = sci.train(X_prose   , Y_prose   , self.type)
        self.first_nonprose_clfs = sci.train(X_nonprose, Y_nonprose, self.type)



    # Model::second_train()
    #
    #
    def second_train(self, data, inds_list, Y):

        """
        Model::first_train()

        Purpose: Train the first pass classifiers (for IOB chunking)

        @param data.      A list of list of strings.
                            - A string is a chunked phrase
                            - An inner list corresponds to one line from the file
        @param inds_list. A list of list of integer indices
                            - assertion: len(data) == len(inds_list)
                            - one line of 'inds_list' contains a list of indices
                                into the corresponding line for 'data'
        @param Y.         A list of concept labels
                            - assertion: there are sum(len(inds_list)) labels
                               AKA each index from inds_list maps to a label
        @return          None
        """


        # Create object that is a wrapper for the features
        feat_o = clicon_features.FeatureWrapper()


        # Extract features
        X = [ feat_o.concept_features(s,inds) for s,inds in zip(data,inds_list) ]
        X = reduce(concat, X)


        # Vectorize labels
        Y = [  Model.labels[y]  for  y  in  Y  ]

        # Vectorize features
        X = self.second_vec.fit_transform(X)


        # Train the model
        self.second_clfs = sci.train(X, Y, self.type)



        
    # Model::predict()
    #
    # @param note. A Note object that contains the data
    def predict(self, note):

        # data   - A list of list of the medical text's words
        data   = note.txtlist()

        # A wrapper for features
        feat_obj = clicon_features.FeatureWrapper(data)

        # First Pass
        bounds = self.first_predict(data, feat_obj)

        # Merge 'B' words with its 'I's to form phrased chunks
        text_chunks, _, hits = clicon_features.generate_chunks(data,bounds)

        # Second Pass
        retVal = self.second_predict(text_chunks,hits,feat_obj)


        return retVal



    # Model::first_predit()
    #
    # @param data. A list of list of words
    # @return      A list of list of IOB tags
    def first_predict(self, data, feat_obj=None):

        # If not given
        if not feat_obj: 
            # Create object that is a wrapper for the features
            feat_obj = clicon_features.FeatureWrapper(data)

        # prose and nonprose - each store a list of sentence feature dicts
        prose    = []
        nonprose = []
        prose_line_numbers    = []
        nonprose_line_numbers = []
        for i,line in enumerate(data):
            # returns both the feature dict AND whether the sentence was prose
            isProse,feats = feat_obj.IOB_features(line)
            if isProse:
                prose.append( feats )
                prose_line_numbers.append(i)
            else:
                nonprose.append( feats )
                nonprose_line_numbers.append(i)


        # Prose (predict, and read predictions)
        prose = flatten(prose)
        nonprose = flatten(nonprose)

        prose_model = self.filename + '1'
        nonprose_model = self.filename + '2'

        sci.write_features(prose_model, prose, None);
        sci.write_features(nonprose_model, nonprose, None)

        sci.predict(prose_model, self.type)
        sci.predict(nonprose_model, self.type)

        

        # Nonprose (predict, and read predictions)
        prose_labels_list    = sci.read_labels(   prose_model, self.type)[self.type]
        nonprose_labels_list = sci.read_labels(nonprose_model, self.type)[self.type]


        # Stitch prose and nonprose labels lists together
        labels = []
        prose_ind    = 0
        nonprose_ind = 0
        p_end_flag = (len(   prose_line_numbers) == 0)
        n_end_flag = (len(nonprose_line_numbers) == 0)

        # Pretty much renaming just for length/readability pruposes
        plist =    prose_labels_list
        nlist = nonprose_labels_list

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



        # IOB labels
        # translate labels_list into a readable format
        # ex. change all occurences of 1 -> 'B'
        tmp = []
        for sentence in data:
            tmp.append([labels.pop(0) for i in range(len(sentence))])
            tmp[-1]= map(lambda l: l.strip(), tmp[-1])
            tmp[-1]= map(lambda l: Model.reverse_IOBs_labels[int(l)],tmp[-1])


        # list of list of IOB labels
        return tmp




    def second_predict(self ,text_chunks, hits, feat_obj=None):

        # If not given
        if not feat_obj:
            # Create object that is a wrapper for the features
            feat_obj = clicon_features.FeatureWrapper()

        # Collect 'hits' to model 'text_chunks' layout
        row_hits   = [ [] for _ in text_chunks ]
        for (i,j) in hits:
            row_hits[i].append(j)


        # rows            - list of list of h-tables (all non-'none' in 2d order)
        # concept_matches - 1-1 correspondence with rows. Numeric labels (1,2,3)
        rows = []
        concept_matches = []
        for i,chunk_inds in enumerate(row_hits):

            # Ignore uninteresting rows
            if not chunk_inds: continue

            # Features for each chunk in the sentence
            row = feat_obj.concept_features(text_chunks[i], chunk_inds)
            rows.append(row)



        # Flatten list of lists
        rows = flatten(rows)


        # Predict using model
        second_pass_model = self.filename + '3'
        sci.write_features(second_pass_model, rows, None)
        sci.predict(second_pass_model, self.type)
        second_pass_labels_list = sci.read_labels(second_pass_model, self.type)


        # Put predictions into format for Note class to read
        retVal = {}
        for t in [1,2,4]: 
        
            # Skip non-predictions
            if t not in second_pass_labels_list: continue
        
            classifications = []
            for hit,concept in zip(hits, second_pass_labels_list[t]):
                concept = Model.reverse_labels[int(concept)]
                i,j = hit

                # Get start position (ex. 7th word of line)
                start = 0
                for k in range(len(text_chunks[i])):
                    if k == j: break;
                    start += len( text_chunks[i][k].split() )

                length = len(text_chunks[i][j].split())
                classifications.append(  (concept, i, start, start+length-1 ) )
        
            retVal[t] = classifications


        # Return values
        return retVal





def concat(a,b):
    """
    list concatenation function (for reduce() purpose)
    """
    return a+b
