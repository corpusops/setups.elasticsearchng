#!/usr/bin/env bash
set -ex
cd /data
EXPIRY=${EXPIRY:-$((365*99))}
OU=es
CA_SUBJ="/OU=$OU/CN=CA/"
SSL_KEY_LENGTH=${SSL_KEY_LENGTH:-2048}
[ ! -e ssl ] && mkdir ssl
cd ssl
gencert() {
    cn=$1
    CERT_SUBJ="${CA_SUBJ}CN=$cn/"
    if [ ! -e root-ca-key.pem ];then
        openssl genrsa -out root-ca-key.pem $SSL_KEY_LENGTH
    fi
    if [ ! -e root-ca.pem ];then
        openssl req -new -x509 -sha256 -key root-ca-key.pem -subj "$CA_SUBJ" -out root-ca.pem -days $EXPIRY
    fi
    if [ ! -e $cn-key-temp.pem ] && [ ! -e $cn-key.pem ];then
        openssl genrsa -out $cn-key-temp.pem $SSL_KEY_LENGTH
    fi
    if [ ! -e $cn-key.pem ];then
        openssl pkcs8 -inform PEM -outform PEM -in $cn-key-temp.pem -topk8 -nocrypt -v1 PBE-SHA1-3DES -out $cn-key.pem
    fi
    if [ ! -e $cn.csr ] && [ ! -e $cn.pem ];then
        openssl req -new -subj "$CERT_SUBJ" -key $cn-key.pem -out $cn.csr
    fi
    if [ ! -e $cn.pem ];then
        openssl x509 -req -in $cn.csr -CA root-ca.pem -CAkey root-ca-key.pem -CAcreateserial -sha256 -out $cn.pem -days $EXPIRY
        echo "changedcrt_$cn"
    fi
    find -maxdepth 1 -name "${cn}*temp" -or -name "${cn}*.csr" -printf 'removing %p\n' -delete
    echo "Generated SSL certs for $cn"
}
for i in $@;do gencert $i;done
# vim:set et sts=4 ts=4 tw=0:
