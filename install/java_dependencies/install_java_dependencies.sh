
if [ "$CLINER_DIR" == "" ];
then
    echo "CLINER_DIR not set..."
    exit
fi

USERNAME=$1
PW=$2

if [ "$USERNAME" == "" ] || [ "$PW" == "" ];
then
    echo -e "\nNOTE: no username or password provided. not installing metamap\n"
else
    echo "INSTALLIN!!"
    #bash metamap_install.sh $USERNAME $PW
fi

#bash lvg_install.sh

#bash stanford-corenlp_install.sh

cd $CLINER_DIR/cliner/lib/java

bash compile.sh

