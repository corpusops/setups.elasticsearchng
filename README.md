# docker based es fullstack deployment using ansible
See playbooks, set your variables and enjoy

```sh
$COPS_ROOT/bin/ansible-playbook -vvv -i $inv deploy.yml \
    -e "{es_servers: dockeres_servers, cops_vars_debug: true}" \
    --skip-tags docker_setup,es_service_stop,configuree,es_service_starte,post,securityadmin
```
