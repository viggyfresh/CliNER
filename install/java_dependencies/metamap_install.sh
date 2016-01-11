
if [ "$CLINER_DIR" == "" ];
then
    echo "CLINER_DIR not set..."
    exit
fi


# this requires multiarch support. 64bit users will be required to add 32 bit support for metamap to work
# just google how to do this. it is pretty straight forward.

USERNAME=$1
PW=$2

# if the java executable is within <parent_dir>/bin/java then JAVA_DIR must be <parent_dir>
JAVA_DIR=$3

if [ "$USERNAME" == "" ] || [ "$PW" == "" ];
then
    echo "no username or password provided. not install metamap"
    exit
fi

# this will set some environment variables aswell as download necessary files
. download.sh $USERNAME $PW

METAMAP_BASE=$CLINER_DIR/cliner/lib/java/metamap/metamapBase

mkdir $METAMAP_BASE

mv $METAMAP_MAIN $METAMAP_BASE/
mv $METAMAP_JAVA_API $METAMAP_BASE/

cd $METAMAP_BASE

tar -xvf "$METAMAP_MAIN"

(  cd public_mm
   bash bin/install.sh < . $JAVA_DIR )

tar -xvf $METAMAP_JAVA_API

( cd public_mm
  bash bin/install.sh < . $JAVA_DIR )

