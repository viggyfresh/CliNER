#!/bin/bash

if [ "$CLINER_DIR" == "" ]
    then
        echo "CLINER_DIR not defined"
    exit
fi

JAVA_DIR="$CLINER_DIR/clicon/lib/java"
OPEN_NLP_LIB=":$JAVA_DIR/openNLP/apache-opennlp-1.6.0/lib/*"
DEPENDENCIES=$OPEN_NLP_LIB


compile() {

    echo "compiling openNLP tokenizer"
    javac -cp $DEPENDENCIES OpenNLPTokenizer.java -d .
}

clean() {

    rm -r opennlp;
    rm *.pyc

}

if [ "$1" == "compile" ]; then

    compile

elif [ "$1" == "clean" ]; then

    clean

else

    echo "invalid arg"

fi

# EOF

