===============================
CliCon
===============================

.. image:: https://badge.fury.io/py/clicon.png
    :target: http://badge.fury.io/py/clicon

.. image:: https://travis-ci.org/tnaumann/clicon.png?branch=master
        :target: https://travis-ci.org/tnaumann/clicon

.. image:: https://pypip.in/d/clicon/badge.png
        :target: https://pypi.python.org/pypi/clicon


Clinical Concept extraction system (CliCon) is an open-source natural language processing system for named entity recognition in clinical text of electronic health records.  CliCon system is designed to follow best practices in clinical concept extraction, as established in i2b2 2010 shared task.  

CliCon is implemented as a two-pass machine learning system for named entity recognition, currently using a Conditional Random Fields (CRF) classifier to establish concept boundaries and a Support Vector Machine (SVM) classifier to establish the type of concept.  

Please note that for optimal performance, CliCon requires the users to obtain a Unified Medical Language System (UMLS) license, since UMLS Metathesaurus is used as one of the knowledge sources for the above classifiers.  


* Free software: BSD license
* Documentation: http://clicon.readthedocs.org.

Features
--------

* TODO



Installation
--------

**Cloning the CliCon git repository:**

:: 

    user@your-machine:~$ git clone https://github.com/mitmedg/CliCon.git
        Cloning into 'CliCon'...
        remote: Counting objects: 1296, done.
        remote: Compressing objects: 100% (503/503), done.
        remote: Total 1296 (delta 812), reused 1253 (delta 781)
        Receiving objects: 100% (1296/1296), 1001.14 KiB | 759 KiB/s, done.
        Resolving deltas: 100% (812/812), done.


**Using an installation script**

Linux users can use an installation script to download and install all the components of this project, including third-party dependencies. Note that cannot get tools and data that require special use agreements (including the i2b2 data and the UMLS tables), which have to be obtained separately.

The following packages need to be on the system for the script to work:

::

    python-pip installer 
    python-virtualenv
    
Some of the required python modules that will be installed by the script have the following dependencies, which also need to be installed:
    
::

    g++
    gfortran
    libopenblas-dev
    liblapack-dev


To invoke the script, first ``cd`` into the ``CliCon`` directory and set the CLICON_DIR environmentn variable:

::    

    user@your-machine:~$ cd CliCon
    user@your-machine:~$ export CLICON_DIR=.
    user@your-machine:~$ source install.sh
    

If the installation script encounters issues, please see the README section corresponding to the failure message. 

If you opt not to use the provided script, you must follow the steps described below, starting with setting up virtual environments and environment variables. Not terribly difficult (we hope!).
    
Please email wboag@cs.uml.edu with your installation questions.


**Step-by-step installation instructions:**


(1) Set up virtualenv

    Setup a virtual environent. You must re-enable the virtual environment every new session.


    example:
        user@your-machine:~$ virtualenv venv_clicon

        user@your-machine:~$ source venv_clicon/bin/activate


    reference
        https://virtualenv.pypa.io/en/latest/





2. Set the CLICON_DIR environment variable

    In order to run CliCon, you must define the CLICON_DIR environment variable.

    user@your-machine:~$ export CLICON_DIR=$(pwd)/CliCon

    **This variable must be the path of the directory created by git.**



3. Install Python dependencies

    This project has dependencies on scientific computation libraries.

    Ensure the following python modules are installed:
        - numpy
        - scikit-learn
        - scipy
        - python-crfsuite
        - nltk  (AND run the NLTK downloader)


        These modules, themselves may have dependencies to install. If necessary, sudo apt-get install these packages

            Ubuntu:
                - g++
                - gfortran
                - libopenblas-dev
                - liblapack-dev


            Mac OSX
                **Tristan should put stuff here**


    example:
        (venv_clicon)user@your-machine:~/CliCon$ sudo apt-get install g++ gfortran libopenblas-dev liblapack-dev -y

        (venv_clicon)user@your-machine:~/CliCon$ pip install numpy scikit-learn scipy nltk python-crfsuite





4. Get i2b2 2010 shared task data

    The Data Use and Confidentiality Agreement with i2b2 forbids us from redistributing their data. In order to gain access, you must go to:

    https://www.i2b2.org/NLP/DataSets/AgreementAR.php

    to register and sign the DUA. Then you will be able to request the data through them.


    Although we cannot provide i2b2 data, there is a sample to demonstrate how the data is formatted (not actual data from i2b2, though). Here is a very basic description of the data formats. It is by no means a complete tutorial.

    Go to the '$CLICON_DIR/examples' directory.

        pretend.txt

            This is a text file. Discharge summaries are written out in plaintext, just like this. It is paired with a concept file, which has its annotations.

        pretend.con

            This is a concept file. It provides annotations for the concepts (problem, treatment, test) of the text file. The format is as follows - each instance of a concept has one line. The line describes the word span, the line number and token numbers of the span (delimited by white space), and the label of the concept.

        pretend.xml

            This is an alternative way to annotate concepts from a discharge summary. Unlike the text/concept files, this format is not in a pair - it provides both the text and annotations for the discharge summary. This format is easier to read.





5. Install GENIA tagger (optional)

    This is an optional part of installation. Adding the GENIA tagger will improve results of the system's predictions, but it could run without it.

    Steps

        1. First you must download the sources for GENIA. Do that with 'wget http://www.nactem.ac.uk/tsujii/GENIA/tagger/geniatagger-3.0.1.tar.gz'

        2. In order to compile the sources, you may need to edit a C++ so that it has an additional include directive. Basically, morph.cpp needs to include cstdlib. This should be able to be accomplished by enterring the geniatagger-3.0.1/ directory and running 'echo "$(sed '1i#include <cstdlib>' morph.cpp)" > morph.cpp'

        3. Compile GENIA. This is simple. Just run 'make'

        4. If you do not have any errors, then the tagger has been built successfully. If there were compile errors, try to resolve them (it'd be one of those "well it works for me" scenarios).

        5. Set the file "$CLICON_DIR/clicon/features/features.config" so that the line that has "GENIA None" is replaced with "GENIA <path-to-tagger-you-just-built>'. This file is how CliCon is able to find and run the tagger.





6. Get UMLS tables (optional)

    This is an optional part of installation. Adding the UMLS tables will improve results of the system's predictions, but it could run without it.

    In order to use the UMLS tables, you must request a license. See:

    http://www.nlm.nih.gov/databases/umls.html

    You will need to get following tables: MRREL, MRCON, MRSTY

    Put these tables in the $CLICON_DIR/umls_tables directory.

    In order to tell CliCon that the tables are there, you must edit the file "$CLICON_DIR/clicon/features" and change the line saying "UMLS None" to "UMLS <path-to-your-umls_tables-dir>".






7. Create 'clicon' executable script for command-line use

    In order to run CliCon (as done in the usage examples), you must run setup.py.

    As long as the Python dependencies are properly installed, you should be able to run 'python $CLICON_DIR/setup.py install'.

    If it works, you should see a brief help message when invoking clicon with the ``--help`` option: 

::

        (venv_clicon)user@your-machine:~/CliCon$ python $CLICON_DIR/setup.py install
        (venv_clicon)user@your-machine:~/CliCon$ clicon --help




8. Run unit tests

    [this section is under construction]



Usage Examples
--------

    End-to-End

        export CLICON_DIR=.
        
        bash install.sh
        
        clicon train $CLICON_DIR/examples/pretend.xml --format xml
        
        clicon predict $CLICON_DIR/examples/pretend.txt
        
        clicon evaluate $CLICON_DIR/examples/pretend.txt --gold $CLICON_DIR/examples --format xml


    i2b2 format

        Example: Train model on i2b2-formatted data
            clicon train $CLICON_DIR/examples/pretend.txt --annotations $CLICON_DIR/examples/pretend.con

        Example: Train model on i2b2-formatted data with SVM grid search (NOTE: Currently does not work with sample data because the sample data is too small for cross validation).
            clicon train $CLICON_DIR/examples/pretend.txt --annotations $CLICON_DIR/examples/pretend.con --grid-search

        Example: Predict concepts and output in i2b2 format
            clicon predict $CLICON_DIR/examples/pretend.txt --out $CLICON_DIR/data/test_predictions/

        example: Evaluation
            clicon evaluate $CLICON_DIR/examples/pretend.txt --gold $CLICON_DIR/examples --predictions $CLICON_DIR/data/test_predictions/ --format i2b2

        example: Change Format
            clicon format $CLICON_DIR/examples/pretend.txt --annotations $CLICON_DIR/data/test_predictions/pretend.con --format xml


    xml format
        Example: Train model on xml-formatted data
            clicon train $CLICON_DIR/examples/pretend.xml --format xml

        Example: Predict concepts and output in xml format
            clicon predict $CLICON_DIR/examples/pretend.txt --out $CLICON_DIR/data/test_predictions/ --format xml

        example: Evaluation
            clicon evaluate $CLICON_DIR/examples/pretend.txt --gold $CLICON_DIR/examples --predictions $CLICON_DIR/data/test_predictions/ --format xml

        example: Change Format
            clicon format $CLICON_DIR/data/test_predictions/pretend.xml --format i2b2




