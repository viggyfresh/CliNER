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



1. virtualenv

    Setup a virtual environent:


    example:
        willie@text-machine:~$ virtualenv venv_clicon

        willie@text-machine:~$ source venv_clicon/bin/activate




2. environment variable

    In order to run CliCon, you must define the CLICON_DIR environment variable.

    **This variable must be the path of the directory creatied by git.**

    example:
        willie@text-machine:~$ pwd
            /home/willie
        willie@text-machine:~$ git clone https://github.com/mitmedg/CliCon.git
            Cloning into 'CliCon'...
            remote: Counting objects: 1296, done.
            remote: Compressing objects: 100% (503/503), done.
            remote: Total 1296 (delta 812), reused 1253 (delta 781)
            Receiving objects: 100% (1296/1296), 1001.14 KiB | 759 KiB/s, done.
            Resolving deltas: 100% (812/812), done.
        willie@text-machine:~$ export CLICON_DIR=/home/willie/CliCon




3. Install CliCon

    This project has dependencies on scientific computation libraries.

    Ensure the following python modules are installed:
        - numpy
        - scikit-learn
        - scipy
        - nltk  (AND run the NLTK downloader)

        **Note, if you are on Ubuntu, then you have to to apt-get the following:
            - g++
            - gfortran
            - libopenblas-dev
            - liblapack-dev
        ***


    example:
        (venv_clicon)willie@text-machine:~/CliCon$ sudo apt-get install g++ gfortran libopenblas-dev liblapack-dev -Y

        (venv_clicon)willie@text-machine:~/CliCon$ pip install numpy scikit-learn scipy nltk

        (venv_clicon)willie@text-machine:~/CliCon$ python setup.py install



4. Get data

    FIXME: Something Something i2b2 agreement.

    **I'll need to ask Kevin how to get data from i2b2**


    OR, if you are Anna Rumshisky, then you know the password to text-machine

    example:
        willie@text-machine:~/CliCon$ scp -r wboag@text-machine:~/CliCon/data/* $CLICON_DIR/data




5. Get UMLS tables (optional)

    **Do-able but I'd need to talk to Kevin about where to get them**




6. Install GENIA tagger (optional)

    **Would take some effort to make this possible. Do-able, but not pretty**




7. Run unit tests

    **We haven't done any unit tests yet**




Usage Examples
--------

    example 1: Sanity Check - Train/Predict on the same file
        (venv_clicon)willie@text-machine:~/CliCon$ clicon train data/concept_assertion_relation_training_data/partners/txt/837898389.txt --annotations data/concept_assertion_relation_training_data/partners/concept/837898389.con

        (venv_clicon)willie@text-machine:~/CliCon$ clicon predict data/concept_assertion_relation_training_data/partners/txt/837898389.txt --out data/test_predictions/

        (venv_clicon)willie@text-machine:~/CliCon$ clicon format data/concept_assertion_relation_training_data/partners/txt/837898389.txt --annotations data/test_predictions/lin/837898389.con  --format xml

