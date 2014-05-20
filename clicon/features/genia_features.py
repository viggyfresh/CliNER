######################################################################
#  CliCon - genia_features.py                                        #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Independent GENIA module                                 #
######################################################################



import clicon_genia_interface



class GeniaFeatures:


    def __init__(self, data):

        """
        Constructor.

        @param data. A list of lists of words (basically a list of sentences)
        """

        # Process all words with GENIA tagger
        self.GENIA_features = clicon_genia_interface.genia(data)

        # For iterating through tagged data
        self.GENIA_counter = 0


    def next_GENIA_line(self):

        """
        next_GENIA_line()

        Purpose: All data was tagged upfront. This allows iteration through data
        """

        # End of list - reset counter & return None
        if self.GENIA_counter == len(self.GENIA_features):
            self.GENIA_counter = 0
            return None

        # Advance to next line
        self.GENIA_counter += 1

        return self.GENIA_features[self.GENIA_counter-1]



    def features(self, sentence, is_prose=True):

        """
        features().

        @param sentence. A list of words to bind features to
        @param is_prose. Mechanism for skipping nonprose (for alignment)
        @return          list of dictionaries (of features)

        Note: All data is tagged upon instantiation of GeniaFeatures object.
              This function MUST take each line of the file (in order) as input
        """

        # Return value is a list of dictionaries (of features)
        features_list = [ {} for _ in sentence ]

        # Get the GENIA features of the current sentence
        genia_feats = self.next_GENIA_line()
        if not genia_feats: genia_feats = self.next_GENIA_line()


        # FIXME
        # Mechanism to allow for skipping nonprose
        # Potential alternative: Let GeniaFeatures boject decide on all nonprose
        if not is_prose: return {}


        for i in range(len(sentence)):

            # Feature: Current word's GENIA features
            keys = ['GENIA-stem','GENIA-POS','GENIA-chunktag']
            curr = genia_feats[i]
            output =  dict( (('curr-'+k, curr[k]), 1) for k in keys if k in curr)

            # Feature: Previous word's GENIA features
            if i == 0:
                output =  dict( (('prev-'+k, '<START>'), 1) for k in keys if k in curr)
            else:
                prev = genia_feats[i]
                output =  dict( (('prev-'+k,   prev[k]), 1) for k in keys if k in prev)

            # Feature: Next word's GENIA stem
            # Note: This is done by updating the previous token's dict
            if i == 0:
                continue
            if i != (len(sentence) - 1):
               features_list[i-1].update( {('next-GENIA-stem',curr['GENIA-stem']) : 1} )
            else:
                features_list[i].update( { ('next-GENIA-stem','<END>') : 1} )

            features_list[i].update(output)


        return features_list
