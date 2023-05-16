#!/usr/bin/env bash
cd $(dirname $(readlink -f $0))
cat | docker-compose exec -T es sh <<'EOF'
set -ex
p="{{es_security_backup_dir}}"
( while ! ( curl https://node:9200 );do sleep 1;done;touch curltest )&
dockerize -wait file://$(pwd)/curltest -timeout 900s
if [ ! -e ${p} ];then mkdir -p ${p};fi
if [ ! -e ${p}/orig ];then {{es_security_cmd}} -backup ${p}/orig;fi
{{es_security_cmd}} -backup ${p}/$(date +"%F_%H.%M.%S")
{{es_security_cmd}} -cd plugins/opensearch-security/securityconfig
EOF
# vim:set et sts=4 ts=4 tw=80:
