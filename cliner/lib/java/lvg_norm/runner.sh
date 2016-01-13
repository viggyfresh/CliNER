
CLASS_PATHS=".:lvg/lib/*"

compile() {

    echo "compiling lvg norm"
    javac -cp $CLASS_PATHS "Norm.java" -d "."

}

run() {

    java -cp $CLASS_PATHS "LvgNormApi.Norm" $@

}

clean() {

    rm -r LvgNormApi
    rm *.pyc
}

if [ "$1" == "compile" ]; then

    compile

elif [ "$1" == "test" ]; then

    compile

    run "bloodied" "battered" "bruised" "dirtiest" "bleeding"

elif [ "$1" == "clean" ]; then

    clean

else

    echo "invalid arg"

fi


# EOF

