
if [ "$CLINER_DIR" = "" ]
    then
        echo "CLINER_DIR not defined"
fi

if [ "$PY4J_DIR_PATH" == "" ]; then
    echo "environment variable PY4J_DIR_PATH not specified"
    echo "please put exact path example .../venv/share/py4j"
    exit
fi

JAVA_DIR="$CLINER_DIR/cliner/lib/java"
METAMAP_DIR="$JAVA_DIR/metamap"
LVG_DIR="$JAVA_DIR/lvg_norm"
STANFORD_DIR="$JAVA_DIR/stanford_nlp"
ENTRY_POINT_DIR="$JAVA_DIR/entry_point"
#OPEN_NLP_DIR="$JAVA_DIR/openNLP"

STANFORD_DEPENDENCIES=":$STANFORD_DIR/stanford-corenlp-full/*:$STANFORD_DIR"
NORMAPI_DEPENDENCIES=":$LVG_DIR/lvg/lib/*:$LVG_DIR"
METAMAP_DEPENDENCIES=":$METAMAP_DIR:$METAMAP_DIR/metamapBase/public_mm/src/javaapi/dist/*"
PY4J_DEPENDENCIES=":$PY4J_DIR_PATH/*"
ENTRY_POINT_DEPENDENCIES=":$ENTRY_POINT_DIR/*"

#OPENNLP_DEPENDENCIES=":$OPEN_NLP_DIR/apache-opennlp-1.6.0/lib/*:$OPEN_NLP_DIR"

#DEPENDENCIES="$PY4J_DEPENDENCIES$METAMAP_DEPENDENCIES$NORMAPI_DEPENDENCIES$STANFORD_DEPENDENCIES$OPENNLP_DEPENDENCIES"
DEPENDENCIES="$ENTRY_POINT_DIR$PY4J_DEPENDENCIES$METAMAP_DEPENDENCIES$NORMAPI_DEPENDENCIES$STANFORD_DEPENDENCIES"


compile() {

    javac -cp $DEPENDENCIES EntryPoint.java -d .
    javac -cp $DEPENDENCIES GateWay.java -d .

}

run() {

    java -cp $DEPENDENCIES gateway.GateWay

}

if [ "$1" == "compile" ]; then

    compile

elif [ "$1" == "clean" ]; then

    rm *.pyc
    rm -r gateway

elif [ "$1" == "test" ]; then

    java -cp $DEPENDENCIES gateway.EntryPoint

elif [ "$1" == "-launch-gateway" ]; then

    run

else

    echo "invalid"

fi




