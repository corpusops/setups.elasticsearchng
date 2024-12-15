DISCLAIMER
============

**UNMAINTAINED/ABANDONED CODE / DO NOT USE**

Due to the new EU Cyber ​​Resilience Act (as European Union), even if it was implied because there was no more activity, this repository is now explicitly declared unmaintained.

The content does not meet the new regulatory requirements and therefore cannot be deployed or distributed, especially in a European context.

This repository now remains online ONLY for public archiving, documentation and education purposes and we ask everyone to respect this.

As stated, the maintainers stopped development and therefore all support some time ago, and make this declaration on December 15, 2024.



# docker based es fullstack deployment using ansible
See playbooks, set your variables and enjoy

```sh
$COPS_ROOT/bin/ansible-playbook -vvv -i $inv deploy.yml \
    -e "{es_servers: dockeres_servers, cops_vars_debug: true}" \
    --skip-tags docker_setup,es_service_stop,configuree,es_service_starte,post,securityadmin
```
