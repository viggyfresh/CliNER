from __future__ import with_statement

import os
import cPickle as pickle
import helper
import sci
import sys

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


    # Constructor
    def __init__(self, filename='awesome.model', type=sci.ALL):
        model_directory = os.path.dirname(filename)

        if model_directory != "":
            helper.mkpath(model_directory)

        self.filename = os.path.realpath(filename)

        # FIXME: Only using scikit's SVM
        self.type = sci.LIN
        



    # Model::train()
    #
    # @param notes. A list of Note objects that has data for training the model
    def train(self, notes):

        # Get the data and annotations from the Note objects
        data   = [  note.txtlist()    for  note  in  notes  ]
        labels = [  note.conlist()    for  note  in  notes  ]
        bounds = [  note.boundlist()  for  note  in  notes  ]

        # Merge data from all files (flatten() only flattens one level deep)
        data   = flatten( data )
        labels = flatten(labels)
        bounds = flatten(bounds)


        # At this point:
        #
        #     data   - A list of list of words straight from the text files
        #     labels - A list of list of concept   labels (1:1 with data)
        #     bounds - A list of list of IOB chunk labels (1:1 with data)
        #

        # Create object that is a wrapper for the features
        feat_obj = clicon_features.FeatureWrapper(data)

        # First pass
        print 'first'
        self.first_train(data, labels, bounds, feat_obj)

        # Second pass
        print 'second'
        self.second_train(data, labels, bounds, feat_obj)

        # Pickle dump
        print 'pickle dump'
        with open(self.filename, "w") as model:
            pickle.dump(self, model)
    



    # Model::train_first()
    #
    # @param notes. A list of Note objects that has data for training the model
    def first_train(self, data, labels, chunks, feat_obj=None):

        print '\tbegin first_train()'

        # (in case not doing both passes) Create feat_obj
        if not feat_obj: 
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
                prose.append( feats )
                prose_line_numbers.append(i)
            else:
                nonprose.append( feats )
                nonprose_line_numbers.append(i)

        print '\tfeatures assigned'

        # Vectorize IOB labels
        label_lu = lambda l: Model.IOBs_labels[l]
        chunks = [map(label_lu, x) for x in chunks]

        print '\tsegregate "chunks" list into prose and nonprose'

        # Segregate chunks into 'Prose CHUNKS' and 'Nonprose CHUNKS'
        # FIXME - very unclear what this is
        prose_ind    = 0
        nonprose_ind = 0
        pchunks = []
        nchunks = []
        p_end_flag = False
        n_end_flag = False
        for i,line in enumerate(chunks):
            if   (not p_end_flag) and (i == prose_line_numbers[prose_ind]):
                pchunks.append(line)
                prose_ind += 1
                if prose_ind == len(prose_line_numbers): p_end_flag = True
            elif (not n_end_flag) and (i == nonprose_line_numbers[nonprose_ind]):
                nchunks.append(line)
                nonprose_ind += 1
                if nonprose_ind == len(nonprose_line_numbers): n_end_flag = True
            else:
                # Should never really get here
                print 'Line #%d is neither prose nor nonprose!' % i
                print line, '\n'


        # Machine Learning file names
        prose_model    = self.filename + '1'
        nonprose_model = self.filename + '2'


        # Flatten feature & label lists
        prose    = flatten(   prose)
        nonprose = flatten(nonprose)
        pchunks  = flatten( pchunks)
        nchunks  = flatten( nchunks)

        sci.write_features(   prose_model,    prose, pchunks)
        sci.write_features(nonprose_model, nonprose, nchunks)

        sci.train(   prose_model, self.type)
        sci.train(nonprose_model, self.type)


        # Pickle dump - Done during train(), not first_train() 
        #with open(self.filename, "w") as model:
        #    pickle.dump(self, model)



    # Model::second_train()
    #
    #
    def second_train(self, data, labels, bounds, feat_obj=None):

        # If not given
        if not feat_obj: 
            # Create object that is a wrapper for the features
            feat_obj = clicon_features.FeatureWrapper()

        # Merge 'B' words with its 'I's (and account for minor change in indices)
        tmp = clicon_features.generate_chunks(data,bounds,labels)

        # text_chunks    - a merged text (highly similiar to data, except merged)
        # concept_chunks - one-to-one concept classification with text_chunks
        # hits           - one-to-one concept token indices  with text_chunks
        text_chunks, concept_chunks, hits = tmp


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

            # Could probably be condensed with some lambda stuff
            row_concepts = []
            for con in concept_chunks[i]:
                if con != 'none':
                    row_concepts.append( Model.labels[con] )

            rows.append(row)
            concept_matches.append( row_concepts )



        # Purpose: Encode something like ('chunk', 'rehabilitation') as a unique
        #          number, as determined by the self.concept_vocab hash table
        rows            = flatten(rows)
        concept_matches = flatten(concept_matches)


        # Write second pass model to file
        second_pass_model = self.filename + '3'
        sci.write_features(second_pass_model, rows, concept_matches)


        # Train the model
        sci.train(second_pass_model, self.type)      # Use LIN


        
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

        self.type = sci.LIN

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




def flatten(ll):

    """
    flatten()

    Purpose: Flatten a list (by one level of depth)
    
    Note: List of list of lists --> list of lists
 
    @param  ll.   List of lists
    @return       flattened list
    """

    return reduce( lambda a,b: a+b, ll )
