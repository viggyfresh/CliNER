from __future__ import with_statement

import os
import cPickle as pickle
import helper
import libml
import sys

from features.clicon_features import clicon_features


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
    def __init__(self, filename='awesome.model', type=libml.ALL):
        model_directory = os.path.dirname(filename)

        if model_directory != "":
            helper.mkpath(model_directory)

        self.filename = os.path.realpath(filename)
        self.type = type
        self.IOB_vocab = {}
        self.concept_vocab = {}
        



    # Model::train()
    #
    # @param notes. A list of Note objects that has data for training the model
    def train(self, notes):

        # Get the data and annotations from the Note object

        # data   - A list of list of the medical text's words
        # labels - A list of list of concepts (1:1 with data)
        data   = []
        labels = []
        bounds = []
        for note in notes:
            data   += note.txtlist()
            labels += note.conlist()
            bounds += note.boundlist()


        # Create object that is a wrapper for the features
        feat_obj = clicon_features.FeatureWrapper(data)

        # First pass
        self.first_train(data, labels, bounds, feat_obj)

        # Second pass
        self.second_train(data, labels, bounds, feat_obj)

        # Pickle dump
        with open(self.filename, "w") as model:
            pickle.dump(self, model)
    



    # Model::train_first()
    #
    # @param notes. A list of Note objects that has data for training the model
    def first_train(self, data, labels, chunks, feat_obj=None):

        # If not given
        if not feat_obj: 
            # Create object that is a wrapper for the features
            feat_obj = clicon_features.FeatureWrapper(data)

        # IOB tagging
        prose    = []
        nonprose = []
        prose_line_numbers    = []
        nonprose_line_numbers = []
        for i,line in enumerate(data):
            isProse,feats = feat_obj.IOB_features_for_sentence(line)
            if isProse:
                prose.append( feats )
                prose_line_numbers.append(i)
            else:
                nonprose.append( feats )
                nonprose_line_numbers.append(i)


        # Encode each feature as a unique number
        for row in prose + nonprose:
            for features in row:
                for feature in features:
                    if feature not in self.IOB_vocab:
                        self.IOB_vocab[feature] = len(self.IOB_vocab) + 1


        # IOB labels
        # A list of a list encodings of concept labels (ex. 'B' => 1)
        # [ [0, 0, 0], [0], [0, 0, 0], [0], [0, 0, 0, 0, 0, 1, 2, 0, 1] ]
        label_lu = lambda l: Model.IOBs_labels[l]
        chunks = [map(label_lu, x) for x in chunks]

        # list of a list of hash tables (all keys & values now numbers)
        feat_lu = lambda f: {self.IOB_vocab[item]:f[item] for item in f}
        prose = [map(feat_lu, x) for x in prose]
        nonprose = [map(feat_lu, x) for x in nonprose]

        # Segregate chunks into 'Prose CHUNKS' and 'Nonprose CHUNKS'
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

        prose_model    = self.filename + '1'
        nonprose_model = self.filename + '2'

        # Use CRF
        libml.write_features(   prose_model,    prose, pchunks, libml.CRF)
        libml.write_features(nonprose_model, nonprose, nchunks, libml.CRF)

        libml.train(   prose_model, libml.CRF)
        libml.train(nonprose_model, libml.CRF)

        #libml.write_features(   prose_model,    prose, pchunks, self.type)
        #libml.write_features(nonprose_model, nonprose, nchunks, self.type)

        #libml.train(   prose_model, self.type)
        #libml.train(nonprose_model, self.type)

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


        # rows is a list of a list of hash tables
        # it is used for holding the features that will be used for training
        rows = []
        concept_matches = []
        row_line = []
        con_line = []
        for ind in range(len((hits))):
            i,j = hits[ind]
            
            # Get features
             
            row_line.append(feat_obj.concept_features(text_chunks[i], j))

            # Corresponding labels (libml encodings of 'treatment','problem',etc)
            con_tmp = concept_chunks[i][j]
            con_tmp = Model.labels[con_tmp]
            con_line.append( con_tmp )

            if (ind == len(hits)-1) or (i != hits[ind+1][0]):
                rows.append(row_line)
                row_line = []
                concept_matches.append(con_line)
                con_line = []


        # Encode each feature as a unique number
        for row in rows:
            for features in row:
                for feature in features:
                    if feature not in self.concept_vocab:
                        self.concept_vocab[feature] = len(self.concept_vocab) + 1


        # Purpose: Encode something like ('chunk', 'rehabilitation') as a unique
        #          number, as determined by the self.concept_vocab hash table
        feat_lu = lambda f: {self.concept_vocab[item]: f[item] for item in f}
        rows = [map(feat_lu, x) for x in rows]


        # Write second pass model to file
        second_pass_model = self.filename + '3'
        mtype = libml.LIN
        libml.write_features(second_pass_model, rows, concept_matches, mtype)
        #libml.write_features(second_pass_model, rows, concept_matches, self.type)


        # Train the model
        libml.train(second_pass_model, mtype)      # Use LIN
        #libml.train(second_pass_model, self.type)


        
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
            isProse,feats = feat_obj.IOB_features_for_sentence(line)
            if isProse:
                prose.append( feats )
                prose_line_numbers.append(i)
            else:
                nonprose.append( feats )
                nonprose_line_numbers.append(i)


        # For applying the (key,value) mapping
        feat_lu = lambda f: {self.IOB_vocab[item]:f[item] for item in f if item in self.IOB_vocab}


        # Prose (predict, and read predictions)
        prose = [map(feat_lu, x) for x in prose]
        prose_model = self.filename + '1'

        libml.write_features(prose_model, prose, None, libml.CRF);
        libml.predict(prose_model, libml.CRF)

        prose_labels_list = libml.read_labels(prose_model, libml.CRF)[libml.CRF]
        

        # Nonprose (predict, and read predictions)
        nonprose = [map(feat_lu, x) for x in nonprose]
        nonprose_model = self.filename + '2'

        libml.write_features(nonprose_model, nonprose, None, libml.CRF);
        libml.predict(nonprose_model, libml.CRF)

        nonprose_labels_list = libml.read_labels(nonprose_model, libml.CRF)[libml.CRF]

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

        # rows            - the format for representing feats for libml
        # concept_matches - labels (ex. 'treatment') encoded for libml
        rows = []
        row_line = []
        for ind in range(len((hits))):
            i,j = hits[ind]
            
            # Get features
            row_line.append(feat_obj.concept_features(text_chunks[i], j))

            if (ind == len(hits)-1) or (i != hits[ind+1][0]):
                rows.append(row_line)
                row_line = []


        # Purpose: Encode something like ('chunk', 'rehabilitation') as a unique
        #          number, as determined by the self.concept_vocab hash table
        feat_lu = lambda f: {self.concept_vocab[item]: f[item] for item in f if item in self.concept_vocab}
        rows = [map(feat_lu, x) for x in rows]

        # Predict using model
        second_pass_model = self.filename + '3'
        mtype = libml.LIN
        libml.write_features(second_pass_model, rows, None, mtype);
        libml.predict(second_pass_model, self.type)
        second_pass_labels_list = libml.read_labels(second_pass_model, mtype)


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

