===============================
CliNER
===============================

Clinical Named Entity Recognition system (CliNER) is an open-source natural language processing system for named entity recognition in clinical text of electronic health records. CliNER system is designed to follow best practices in clinical concept extraction, as established in i2b2 2010 shared task.

CliNER is implemented as a sequence classification task, where every token is predicted IOB-style as either: Problem, Test, Treatment, or None. Coomand line flags let you specify two different sequence classification algorithms:
    1. CRF (default) - with linguistic and domain-specific features
    2. LSTM

Please note that for optimal performance, CliNER requires the users to obtain a Unified Medical Language System (UMLS) license, since UMLS Metathesaurus is used as one of the knowledge sources for the above classifiers.


* Free software: Apache v2.0 license
* Documentation: http://cliner.readthedocs.org.



Installation
--------


        > pip install -r requirements.txt

        > wget http://text-machine.cs.uml.edu/cliner/samples/doc_1.txt

        > wget http://text-machine.cs.uml.edu/cliner/models/silver.model;  mv silver.model models/silver.model

        > cliner predict --txt doc_1.txt --out data/predictions --model models/silver.model  --format i2b2



Optional Resources
--------

There are a few external resources that are not packaged with CliNER but can improve prediction performance for feature extraction with the CRF.

    GENIA

        **Why would I want this?** The GENIA tagger is a tool similar to CliNER but designed for Biomedical text. Depending on the domain of your data, this tool's pretrained model may or may not be able to improve performance for CliNER as it detects concepts.
        

        **reference** http://www.nactem.ac.uk/tsujii/GENIA/tagger/

        The GENIA tagger identifies named entities in biomedical text.
        
        > wget http://www.nactem.ac.uk/tsujii/GENIA/tagger/geniatagger-3.0.2.tar.gz
        
        > tar xzvf geniatagger-3.0.2.tar.gz
        
        > cd geniatagger-3.0.2
        
        > make
        
        
        **Edit config.txt so that GENIA references the geniatagger executable just built. (e.g. "GENIA   /someuser/CliNER/geniatagger-3.0.2/geniatagger")**

    UMLS
    
        **Why would I want this?** The UMLS, or Unified Medical Language System, is a very comprehensive database of various medical terms and concepts. Access to it would allow CliNER to leverage domain-specific knowledge.

        SORRY! This resource is contains potentially sensitive clinical data, and requires a confidentiality agreement. We can't do that part for you. Please see "Additional Resources" portion of this readme for instructions on how to obtain the UMLS tables.
        
        In order to use the UMLS tables, you must request a license. 
        See: http://www.nlm.nih.gov/databases/umls.html

        How to obtain UMLS tables:
        
        - Download all the files from: https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html
        - Unzip mmsys.zip into a folder and put all other files downloaded into that folder.
        - Execute run_linux.sh and select 'Install UMLS' on gui.
        - Choose a destination for umls directory, hit 'Ok' and then 'Create New Config'.
        - Accept the agreement.
        - Select 'Only Active UMLS Sources' as your default subset.
        - Select 'Done' at the top right of gui pane and then select 'Begin Subset'.
        - This process may take a while, the directory '<Destination_Directory_Path>/<UMLS VERSION>/META' should contain the necessary files needed.
        
        You will need to get following tables: **LRARBR, MRREL.RRF, MRCONSO.RRF, MRSTY.RRF**
        
        **Put these tables in the $CLINER_DIR/umls_tables directory.**

        In order to tell CliNER that the tables are there, you must edit the file "$CLINER_DIR/config.txt" and change the line saying "UMLS  None" to "UMLS <path to dir containing tables>".

        **The database will be built from the tables when CliNER is run for the first time.**
      
        *reference https://www.nlm.nih.gov/research/umls/quickstart.html*

Please email wboag@cs.uml.edu with your installation issues/questions.


Optional Tools
--------


VIRTUALENV

    **Why would I want this?** Virtual environments are good practice for when you want to install particular versions of python packages on a per-project basis. They modify local include paths, rather than the system-wide one. They are especially useful when you do not want to disturb other users on a shared server or when your own projects require different library version numbers.

    Setup a virtual environent, and make sure you specify that we're using Python 2.7

        virtualenv venv_cliner -p /usr/bin/python2.7

    You must re-enable the virtual environment every new session.

        source venv_cliner/bin/activate


    **reference** https://virtualenv.pypa.io/en/latest/


Out-of-the-Box Model
--------

Although i2b2 licensing prevents us from releasing our cliner models trained on i2b2 data, we generated some comprable models from automatically-annotated MIMIC II text.

This silver MIMIC model can be found at https://github.com/text-machine-lab/CliNER/blob/master/models/mimic-silver.cliner.tgz


Additional Resources
--------

These are resources that require login credentials to access secure data, so we can't provide you with them directly.


i2b2 2010 shared task data

    The Data Use and Confidentiality Agreement (DUA) with i2b2 forbids us from redistributing the i2b2 data. In order to gain access to the data, you must go to:

    https://www.i2b2.org/NLP/DataSets/AgreementAR.php

    to register and sign the DUA. Then you will be able to request the data through them.



Example Data
--------

Although we cannot provide i2b2 data, there is a sample to demonstrate how the data is formatted (not actual data from i2b2, though).

    examples/pretend.txt

This is a text file. Discharge summaries are written out in plaintext, just like this. It is paired with a concept file, which has its annotations.

    examples/pretend.con

This is a concept file. It provides annotations for the concepts (problems, treatments, and tests) of the text file. The format is as follows - each instance of a concept has one line. The line shows the text span, the line number, token numbers of the span (delimited by white space), and the label of the concept.

    examples/pretend.xml

This is an alternative way to annotate concepts from a discharge summary. This format is easier to read in context because the concepts are embedded in the text document. Note that the .xml files still function as a concept file and will always be paried with a corresponding text file (despite redundancies).



Usage
--------

Here are some use cases:

(1) Check that CliNER installed correctly

This help message will list the options available to run (train/predict/evaluate)

    cliner --help


(2) See an end-to-end run of train/predict/evaluate

This script demonstrates a simple run of training, predicting, and evaluating the system.

   bash examples/demo.sh


(3) Training

These examples demonstrate how to build a CliNER model which can then be used for predicting concepts in text files.

    cliner train --txt examples/pretend.txt --annotations examples/pretend.con --format i2b2 --model models/foo.model

This example trains a very simple CliNER model. The (pretend.txt, pretend.con) pair form as the only document for learning to identify concepts. We must specify that these files are i2b2 format (even though the .con extension implies i2b2 format, you can never be too careful). The CliNER model is then serialized to models/foo.model as specified.

Please note that multiple files could be passed by enclosing them as a glob within "" quotes.


    cliner train --txt examples/pretend.txt --annotations examples/pretend.con --format i2b2 --model models/foo.model --grid-search

This example doesn't actually run. The input file pretend.con is too small that there are not enough data points to perform a grid search over. However, if you do wish to run grid search, it is as simple as using the --grid-search flag.


    cliner train --txt examples/pretend.txt --annotations examples/pretend.xml --format xml --model models/foo.model

Here's one last example for training. In this example, we trained on xml-annotated data. Hopefully it's now clear why we always pair the .xml file with a .txt (it makes the interface much more consistent across data formats).


(4) Prediction

Once your CliNER model is built, you can use it to predict concepts in text files.

    cliner predict --txt examples/pretend.txt --out data/test_predictions/ --format i2b2 --model models/foo.model

In this example, we use the models/foo.model CliNER model that we built up above. This model is used to predict concepts in i2b2 format for the pretend.txt file. This generates a file named "pretend.con" and stores it in the specified output directory.

Notice that we trained and predicted on the same file, so we definitely overfit our way into a perfect match.

    cliner predict --txt examples/pretend.txt --out data/test_predictions/ --format xml  --model models/foo.model

Once again, here's the same example as above, but with predicting xml annotations.


(5) Evaluation

This allows us to evaluate how well CliNER does by comparing it against a gold standard.

    cliner evaluate --txt examples/pretend.txt --gold examples --predictions data/test_predictions/ --format i2b2

Evaluate how well the system predictions did for given discharge summaries. The prediction and reference driectories are provided with the --predictions and --gold flags, respectively. Both sets of data must be in the same format, and that format must be specified - in this case, they are both i2b2. This means that both the examples and data/test_predictions directories contain the file pretend.con.




Notes
--------

The cliner pipeline assumes that the clinical text has been preprocessed to be tokenized, as in accordance with the i2b2 format. I have included a simple tokenization script (see: `tools/tok.py`) that you can use or modify as you wish.

The silver model does come with some degradation of performance. Given that the alternative is no model, I think this is okay, but be aware that if you have the i2b2 training data, then you can build a model that performs even better on the i2b2 test data.


Original Model (trained on i2b2-train data with UMLS + GENIA feats)

    TESTING 1.1 -  Exact span for all concepts together
                         TP    FN    FP   Recall Precision F1
    Class Exact Span -> 23358 4904  7696  0.826  0.752     0.788

    TESTING 1.2 -  Exact span for separate concept classes
                                                      TP    FN    FP   Recall   Precision  F1
    Exact Span With Matching Class for Problem   ->  9478  2291  3077  0.805    0.755      0.779
    Exact Span With Matching Class for Treatment ->  6881  1402  2398  0.831    0.742      0.784
    Exact Span With Matching Class for Test      ->  6999  1211  2221  0.852    0.759      0.803


Silver Model (trained on mimic data that was annotated by Original Model)

    TESTING 1.1 -  Exact span for all concepts together
                         TP    FN    FP    Recall Precision F1
    Class Exact Span -> 20771 5504  10283  0.791  0.669     0.725

    TESTING 1.2 -  Exact span for separate concept classes
                                                     TP    FN    FP   Recall  Precision  F1
    Exact Span With Matching Class for Problem   -> 8735  2875  3820  0.752   0.696      0.7229464100972481
    Exact Span With Matching Class for Treatment -> 5961  1278  3318  0.823   0.642      0.721758082092263
    Exact Span With Matching Class for Test      -> 6075  1351  3145  0.818   0.659      0.7299050823020545
