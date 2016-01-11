
if [ "$CLINER_DIR" == "" ];
then
    echo "CLINER_DIR not set..."
    exit
fi

wget http://lexsrv3.nlm.nih.gov/LexSysGroup/Projects/lvg/2013/release/lvg2013.tgz .

mv lvg2013.tgz $CLINER_DIR/cliner/lib/java/lvg_norm/

tar -xvf $CLINER_DIR/cliner/lib/java/lvg_norm/lvg2013.tgz -C $CLINER_DIR/cliner/lib/java/lvg_norm/

cd $CLINER_DIR/cliner/lib/java/lvg_norm/

mv lvg2013 lvg

cd lvg

sed -i 's|gtar|tar|g' install/bin/install_linux.sh

bash install_linux.sh

