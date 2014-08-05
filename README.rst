===============================
CliCon
===============================

.. image:: https://badge.fury.io/py/clicon.png
    :target: http://badge.fury.io/py/clicon

.. image:: https://travis-ci.org/tnaumann/clicon.png?branch=master
        :target: https://travis-ci.org/tnaumann/clicon

.. image:: https://pypip.in/d/clicon/badge.png
        :target: https://pypi.python.org/pypi/clicon


A short description of CliCon.

* Free software: BSD license
* Documentation: http://clicon.readthedocs.org.

Features
--------

* TODO




Installation
--------


Installation Script

    For Ubuntu users, there is a script that should be able to download most of the pieces of this project. Note, it cannot get priveleged tools (such as the i2b2 data and the UMLS tables) - you must get those two pieces yourself.

    To run the script, copy 'install.sh' from Github and enter the directory you'd like to house this project. Run the script with **source install.sh** NOTE: The script will git clone CliCon for you, so do not do that yourself if you use the script.

    The script will try to download CliCon's third party dependencies and will report back what tools could/couldn't be acquired. Ideally, it will get everything except for the i2b2 data and the UMLS tables.

    In the event that you run the script but encounter issues, please see the README section that corresponds to the failure's message. 

    It is entirely likely that there are unforseen bugs. If you experience "strange" behavior (or if this document is just unclear in general), please email me at wboag@cs.uml.edu with your installation questions.

    If you do not run the script, you must follow each of these steps and configure things such as virtual environments and environment variables. Not terribly difficult (we hope!).




1. virtualenv

    Setup a virtual environent:


    reference
        https://virtualenv.pypa.io/en/latest/


    example:
        user@your-machine:~$ virtualenv venv_clicon

        user@your-machine:~$ source venv_clicon/bin/activate




2. environment variable

    In order to run CliCon, you must define the CLICON_DIR environment variable.

    **This variable must be the path of the directory created by git.**

    example:
        user@your-machine:~$ git clone https://github.com/mitmedg/CliCon.git
            Cloning into 'CliCon'...
            remote: Counting objects: 1296, done.
            remote: Compressing objects: 100% (503/503), done.
            remote: Total 1296 (delta 812), reused 1253 (delta 781)
            Receiving objects: 100% (1296/1296), 1001.14 KiB | 759 KiB/s, done.
            Resolving deltas: 100% (812/812), done.
        user@your-machine:~$ export CLICON_DIR=$(pwd)/CliCon




3. Install Pytohn Dependencies

    This project has dependencies on scientific computation libraries.

    Ensure the following python modules are installed:
        - numpy
        - scikit-learn
        - scipy
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

        (venv_clicon)user@your-machine:~/CliCon$ pip install numpy scikit-learn scipy nltk





4. Get i2b2 data

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






7. Create 'clicon' command for CLI

    In order to run CliCon (as done in the usage examples), you must run setup.py.

    This is very simple. As long as the python dependencies are properly installed, you can run 'python $CLICON_DIR/setup.py install'.

    If it works, you should see a tiny help message from enterring 'clicon --help'

    example:

        (venv_clicon)user@your-machine:~/CliCon$ python $CLICON_DIR/setup.py install

        (venv_clicon)user@your-machine:~/CliCon$ clicon --help




8. Run unit tests

    **We haven't done any unit tests yet**




Usage Examples
--------

    CliCon is a Machine Learning interface for concept extraction. It is able to train and predict on data. It can also change formats from i2b2 <-> xml. Soon, it will also provide an evaluation metric to see how correct its predictions actually are.

    example 1: Sanity Check - Train/Predict on the same file
        (venv_clicon)user@your-machine:~/CliCon$ clicon train $CLICON_DIR/examples/pretend.txt --annotations $CLICON_DIR/examples/pretend.con

        (venv_clicon)user@your-machine:~/CliCon$ clicon predict $CLICON_DIR/examples/pretend.txt --out $CLICON_DIR/data/test_predictions/

        (venv_clicon)user@your-machine:~/CliCon$ clicon format $CLICON_DIR/examples/pretend.txt --annotations $CLICON_DIR/data/test_predictions/lin/pretend.con --format xml

