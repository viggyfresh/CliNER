
# setting login
export UTS_USERNAME=$1
export UTS_PASSWORD=$2

# get proessor type
PROC_TYPE=$(uname -m)

# determine metamap java api version
if [ $PROC_TYPE = "x86_64" ]; then
    # 64 bit
    METAMAP_JAVA_API_HTTP=https://metamap.nlm.nih.gov/download/public_mm_linux_javaapi_64bit_2014.tar.bz2
    METAMAP_JAVA_API=public_mm_linux_javaapi_64bit_2014.tar.bz2
else
    # 32 bit
    METAMAP_JAVA_API_HTTP=https://metamap.nlm.nih.gov/download/public_mm_linux_javaapi_2014.tar.bz2
    METAMAP_JAVA_API=public_mm_linux_javaapi_2014.tar.bz2
fi

# need to get full metamap version to install java api
METAMAP_MAIN_HTTP=https://metamap.nlm.nih.gov/download/public_mm_linux_main_2014.tar.bz2
METAMAP_MAIN=public_mm_linux_main_2014.tar.bz2

# script used to download stuff. provided by folks at NIH
DOWNLOAD=umls_download_scripts/curl-uts-download.sh

# downloading metamap
. $DOWNLOAD $METAMAP_MAIN_HTTP
. $DOWNLOAD $METAMAP_JAVA_API_HTTP

export METAMAP_JAVA_API
export METAMAP_MAIN

unset UTS_USERNAME
unset UTS_PASSWORD

