#!/bin/bash

if [ "$CLINER_DIR" == "" ]
    then
        echo "CLINER_DIR not defined"
    exit
fi

JAVA_DIR="$CLINER_DIR/cliner/lib/java"
METAMAP_DIR="$JAVA_DIR/metamap"
LVG_DIR="$JAVA_DIR/lvg_norm"

NORMAPI_DEPENDENCIES=":$LVG_DIR/lvg/lib/*:$LVG_DIR"
METAMAP_DEPENDENCIES=":metamapBase/public_mm/src/javaapi/dist/*"
DEPENDENCIES=$NORMAPI_DEPENDENCIES$METAMAP_DEPENDENCIES

compile() {

    echo "compiling MetaMap"
    javac Cartesian.java -d .
    javac -cp $DEPENDENCIES MetaMap.java -d .


}

clean() {

    rm -r metamap
    rm *.pyc

}

run() {

    java -cp $DEPENDENCIES metamap.MetaMap $1

}


if [ "$1" == "compile" ]; then

    compile

elif [ "$1" == "clean" ]; then

    clean

elif [ "$1" == "run" ]; then

    run "$2"

else

    echo "invalid arg"

fi

# EOF

