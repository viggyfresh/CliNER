from __future__ import with_statement

import os
import cPickle as pickle
import helper
import libml

import clicon_features


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
    # @param notes. A Note object that has data for training the model
    def train(self, notes):

        # Get the data and annotations from the Note object

        # data   - A list of list of the medical text's words
        # labels - A list of list of concepts (1:1 with data)
        data   = []
        labels = []
        chunks = []
        for note in notes:
            data   += note.txtlist()
            labels += note.conlist()
            chunks += note.boundlist()


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


        # each list of hash tables (one list per line in file)
        #for row in rows:
        for row in prose + nonprose:
            # each hash table (one hash table per word in the line)
            for features in row:
                # each key (tuple) pair in hash table (one key per feature)
                for feature in features:
                    # assigning a unique number to each (feature,value) pair
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

        libml.write_features(   prose_model,    prose, pchunks, self.type)
        libml.write_features(nonprose_model, nonprose, nchunks, self.type)

        libml.train(   prose_model, self.type)
        libml.train(nonprose_model, self.type)


        ####################
        #    Second Pass   #
        ####################


        # IOB labels
        # undo encodings of concept labels (ex. 1 => 'B')
        label_lu = lambda l: Model.reverse_IOBs_labels[l]
        chunks = [map(label_lu, x) for x in chunks]


        # Merge 'B' words with its 'I's (and account for minor change in indices)
        tmp = feat_obj.generate_chunks(data,chunks,labels)

        # text_chunks    - a merged text (highly similiar to data, except merged)
        # concept_chunks - one-to-one concept classification with text_chunks
        # hits           - one-to-one concept token indices  with text_chunks
        text_chunks, concept_chunks, hits = tmp


        # rows is a list of a list of hash tables
        # it is used for holding the features that will be used for training
        rows = []
        text_matches    = []
        concept_matches = []
        for hit in hits:
            i,j = hit
            rows.append(feat_obj.concept_features(text_chunks[i], j))

            text_matches.append(text_chunks[i][j])
            concept_matches.append(concept_chunks[i][j])


        # each hash table (one hash table per word in the line)
        for features in rows:
            # each key (tuple) pair in hash table (one key per feature)
            for feature in features:
                # assigning a unique number to each (feature,value) pair
                if feature not in self.concept_vocab:
                    self.concept_vocab[feature] = len(self.concept_vocab) + 1


        # Encode concept labels to numbers (ex. 'treatment' => 1)
        # NOTE: There are no longer 'none' classifications
        # ex. [1,2,1]
        labels = []
        for con in concept_matches:
            #print con
            tmp = Model.labels[con]
            labels.append(tmp)


        # Purpose: Encode something like ('chunk', 'rehabilitation') as a unique
        #          number, as determined by the self.concept_vocab hash table
        #feat_lu = lambda f: {self.concept_vocab[item]:f[item] for item in f}
        #rows = [map(feat_lu, x) for x in rows]
        tmp_rows = []
        for fdict in rows:
            #print fdict
            tmp =  {self.concept_vocab[key]:fdict[key] for key in fdict}
            tmp_rows.append(tmp)
        rows = tmp_rows

        # Write second pass model to file
        second_pass_model = self.filename + '3'
        libml.write_features(second_pass_model, [rows], [labels], self.type)
        libml.train(second_pass_model, self.type)


        # Pickle dump
        with open(self.filename, "w") as model:
            pickle.dump(self, model)



        
    # Model::predict()
    #
    # @param note. A Note object that contains the data
    def predict(self, note):

        # data   - A list of list of the medical text's words
        data   = note.txtlist()


        # A wrapper for features
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


        # FIXME
        # Not sure if this should be reset, but it makes sense to me to do it
        # But why is it a data member if it shouldnt persist
        self.IOB_vocab = {}

        # Create a mapping of each (feature,value) pair to a unique number
        for row in prose + nonprose:
            for features in row:
                for feature in features:
                    if feature not in self.IOB_vocab:
                        self.IOB_vocab[feature] = len(self.IOB_vocab) + 1


        # For applying the (key,value) mapping
        feat_lu = lambda f: {self.IOB_vocab[item]:f[item] for item in f if item in self.IOB_vocab}


        # Prose (predict, and read predictions)
        prose = [map(feat_lu, x) for x in prose]
        prose_model = self.filename + '1'

        libml.write_features(prose_model, prose, None, self.type);
        libml.predict(prose_model, self.type)

        prose_labels_list = libml.read_labels(prose_model, self.type)
        

        # Nonprose (predict, and read predictions)
        nonprose = [map(feat_lu, x) for x in nonprose]
        nonprose_model = self.filename + '2'

        libml.write_features(nonprose_model, nonprose, None, self.type);
        libml.predict(nonprose_model, self.type)

        nonprose_labels_list = libml.read_labels(nonprose_model, self.type)


        # Stitch prose and nonprose labels lists together
        labels_list = {}


        # FIXME - incorrect
        for key in libml.bits(self.type):

            # FIXME - workaround for key
            #if not prose_labels_list[key]: 
            #    labels_list[2] = {}
            #    continue

            labels = []
            prose_ind    = 0
            nonprose_ind = 0
            p_end_flag = (len(   prose_line_numbers) == 0)
            n_end_flag = (len(nonprose_line_numbers) == 0)

            # Pretty much renaming just for length/readability pruposes
            plist =    prose_labels_list[key]
            nlist = nonprose_labels_list[key]

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
   
            labels_list[key] = labels



        # IOB labels
        # translate labels_list into a readable format
        # ex. change all occurences of 1 -> 'B'
        for t, labels in labels_list.items():
            if not labels_list[t]: continue
            tmp = []
            for sentence in data:
                tmp.append([labels.pop(0) for i in range(len(sentence))])
                tmp[-1]= map(lambda l: l.strip(), tmp[-1])
                tmp[-1]= map(lambda l: Model.reverse_IOBs_labels[int(l)],tmp[-1])
                labels_list[t] = tmp



        #print '-'*80
        #print "\nlabels_list"
        #print labels_list
        #print "\n" + "-" * 80


        # Reminder: list of list of words (line-by-line)
        text = data

        # List of list of tokens (similar to 'text', but concepts are grouped)
        chunked   = {1:[], 2:[], 4:[]}
        hits_list = {1:[], 2:[], 4:[]}


        # Create tokens of full concept boundaries for second classifier
        for t,chunks in labels_list.items():

            # FIXME - workaround
            if not labels_list[t]: continue

            # Merge 'B' words with its 'I's to form phrased chunks
            tmp = feat_obj.generate_chunks(text,chunks)

            # text_chunks    - a merged text 
            # place_holder   - ignore. It has a value of []
            # hit_tmp        - one-to-one concept token indices with text_chunks
            text_chunks, place_holder, hits = tmp

            print '\n'*5 + '-'*80 + '\n'*5
            print hits
            for foo,bar in enumerate(text_chunks):
                print foo, ': ', bar
            print hits

            # Store chunked text
            chunked[t]   = text_chunks
            hits_list[t] = hits


        #############################
        #        Second Pass        #
        #############################


        # Predict classification for chunks
        # FIXME - possible error - only predicts on 4
        text_chunks        =   chunked[1]
        hits               = hits_list[1]

        #print labels_list


        # rows         - the format for representing feats for machine learning
        # text_matches - the phrase chunks corresponding to classifications
        rows = []
        text_matches    = []
        for hit in hits:
            i,j = hit
            rows.append(feat_obj.concept_features(text_chunks[i], j))
            text_matches.append(text_chunks[i][j])


        #print text_matches


        # FIXME
        # Not sure if this should be reset, but it makes sense to me to do it
        # But why is it a data member if it shouldnt persist
        self.concept_vocab = {}

        for features in rows:
            for feature in features:
                if feature not in self.concept_vocab:
                    self.concept_vocab[feature] = len(self.concept_vocab) + 1

        # Purpose: Encode something like ('chunk', 'rehabilitation') as a unique
        #          number, as determined by the self.concept_vocab hash table
        tmp_rows = []
        for fdict in rows:
            #print fdict
            tmp =  {self.concept_vocab[key]:fdict[key] for key in fdict}
            tmp_rows.append(tmp)
        rows = tmp_rows


        #print rows


        # Predict using model
        second_pass_model = self.filename + '3'
        libml.write_features(second_pass_model, [rows], None, self.type);
        libml.predict(second_pass_model, self.type)
        second_pass_labels_list = libml.read_labels(second_pass_model, self.type)


        # FIXME - I probably shouldn't have to do this
        # I don't know why it doesn't use all ML libs 
        for t in [1,2,4]:
            if t not in second_pass_labels_list:
                second_pass_labels_list[t] = []


        #print second_pass_labels_list

        # translate labels_list into a readable format
        # ex. change all occurences of 0 -> 'none'
        for t, labels in second_pass_labels_list.items():

            if labels == []:
                # FIXME - this means that there are ML libs not being used
                #print '\nNot predicting on: ', t, '\n'
                continue

            tmp = []
            for sentence in [text_matches]:
                tmp.append([labels.pop(0) for i in range(len(sentence))])
                tmp[-1] = map(lambda l: l.strip(), tmp[-1])
                tmp[-1] = map(lambda l: Model.reverse_labels[int(l)],tmp[-1])
                second_pass_labels_list[t] = tmp


        #print second_pass_labels_list


        # Put predictions into format for Note class to read
        retVal = {}
        for t in [1,2,4]: 

            # Skip non-predictions
            if second_pass_labels_list[t] == []: continue

            classifications = []
            for hit,concept in zip(hits, second_pass_labels_list[t][0]):
                i,j = hit
                length = len(text_chunks[i][j].split())
                #print (concept, i, j, j+length-1 )
                classifications.append(  (concept, i+1, j, j+length-1 ) )

            retVal[t] = classifications


        # Return values
        return retVal

