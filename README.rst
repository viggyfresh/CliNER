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



2. Get data

    FIXME: Something Something i2b2 agreement.


    OR, if you are Anna Rumshisky, then you know the password to text-machine
    example:
        willie@text-machine:~/CliCon$ scp -r wboag@text-machine:~/clicon_data/* data



3. environment variable

    In order to run CliCon, you must define the CLICON_DIR environment variable.
    **This variable must be the path of the directory creatied by git.**

    example:
        willie@text-machine:~$ pwd
            /home/willie
        wboag@cs1:~$ git clone https://github.com/mitmedg/CliCon.git
            Cloning into 'CliCon'...
            remote: Counting objects: 1296, done.
            remote: Compressing objects: 100% (503/503), done.
            remote: Total 1296 (delta 812), reused 1253 (delta 781)
            Receiving objects: 100% (1296/1296), 1001.14 KiB | 759 KiB/s, done.
            Resolving deltas: 100% (812/812), done.
        willie@text-machine:~$ export CLICON_DIR=/home/willie/CliCon



3. Get UMLS tables (optional)

    Optional:


    Note: If you get an error that looks like

        Traceback (most recent call last):
           ...
            import SQLookup
          File "/home/willie/CliCon/clicon/features/SQLookup.py", line 25, in <module>
            c = SQLConnect()
          File "/home/willie/CliCon/clicon/features/SQLookup.py", line 17, in SQLConnect
            create_sqliteDB.create_db()
          File "/home/willie/CliCon/clicon/features/create_sqliteDB.py", line 11, in create_db
            conn = sqlite3.connect( db_path )
        sqlite3.OperationalError: unable to open database file

    Then the system thinks you have UMLS databases when you actually do not.
    To solve this, you need to change the file $CLICON_DIR/clicon/features/features.config to look like:

        GENIA False
        UMLS  False

    If that does not work, then check to make sure your CLICON_DIR variable is correct.



4. Install GENIA tagger (optional)




5. Switch to working branch (TEMPORARY)

    example:
        willie@text-machine:~/CliCon$ git checkout parameterization



6. Install CliCon

    example:
        (venv_clicon)willie@text-machine:~/CliCon$ python setup.py install


    I had to pip install:
        - numpy
        - scikit-learn
        - scipy
        - nltk  (AND run the NLTK downloader)

    I had to apt-get install:
        - g++
        - gfortran
        - libopenblas-dev
        - liblapack-dev


7. Give it a test run

    example 1:
        (venv_clicon)willie@text-machine:~/CliCon$ clicon train

