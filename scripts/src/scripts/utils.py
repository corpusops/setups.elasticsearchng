#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import datetime

import os
import json
from collections import OrderedDict
import requests
import logging
import copy
import secrets
import re
import time
import random
import string
from http.client import HTTPConnection
import ldap3


def as_bool(value):
    if isinstance(value, str):
        return bool(re.match("^(y|o|1|t)", value.lower()))
    else:
        return bool(value)


L = logging.getLogger(__name__)
default_dry_run = os.environ.get('ES_INVITE_DRYRUN',
                                 os.environ.get("DRYRUN", "1"))
_default = default = object()
_vars = {}

ES_URL = os.environ.get('ES_URL', '')
ES_API = '/'

ES_USERNAME = os.environ.get('ES_USERNAME', '').strip()
ES_PASSWORD = os.environ.get('ES_PASSWORD', '').strip()
LOGLEVEL = os.environ.get("LOGLEVEL", "info").upper()
REQUEST_DEBUG = as_bool(os.environ.get("REQUEST_DEBUG", ""))


def filter_dict(d, filters=None):
    if filters is None:
        filters = [a for a in d]
    ret = {}
    for i in d:
        if i not in filters:
            continue
        ret[i] = d[i]
    return ret


def toggle_debug(activate=None, loglevel=None, debuglevel=logging.DEBUG, errorlevel=logging.INFO):
    if loglevel is None:
        loglevel = LOGLEVEL
    loglevel = loglevel.upper()
    if activate is None:
        activate = not _vars.get("debug")
    dl = debuglevel <= logging.DEBUG and 1 or 0
    lvl = activate and debuglevel or errorlevel
    HTTPConnection.debuglevel = dl
    for req_log in [
        logging.getLogger(lg) for lg in (
            "urllib3",
            "urllib3.connectionpool",
            "equests.packages.urllib3",
        )
    ]:
        req_log.propagate = activate
        req_log.setLevel(lvl)
    _vars["debug"] = activate
    logging.getLogger("").setLevel(loglevel)
    return activate


def setup_logging(loglevel=None):
    logging.basicConfig()
    debuglvl = REQUEST_DEBUG and logging.DEBUG or logging.INFO
    toggle_debug(True, debuglevel=debuglvl, loglevel=loglevel)


class HarborRequestError(AssertionError):
    """."""

    def __init__(self, msg=None, resp=None, *a, **kw):
        AssertionError.__init__(self, msg, *a, **kw)
        self.resp = resp


def es_api(path,
               method='get',
               json=default,
               force_uri=False,
               force_url=False,
               userheaders=default,
               expect_msg=None,
               expect=None,
               *a, **kw):
    """
    to auth yourself, login in a es session with your user
    and sneak the requests to /apî,
    and grab the value of cookies which must look like "_gorilla_crsf=xxx, sid=xxxx"
    export it ao $ES_COOKIE env var
    """
    if userheaders is default:
        userheaders = get_userheaders()
    url = (not force_url) and ES_URL or ''
    uri = (not force_uri) and ES_API or ''
    uri = url + uri + path
    if json is not default:
        kw['json'] = json
    headers = kw.setdefault('headers', {})
    if isinstance(userheaders, dict):
        _ = [headers.setdefault(h, v) for h, v, in userheaders.items()]
    if ES_COOKIE:
        headers.setdefault('Cookie', ES_COOKIE)
    else:
        kw['auth'] = (ES_USERNAME, ES_PASSWORD)
        resp = getattr(requests, method.lower())(uri, *a, **kw)
    if expect:
        if not isinstance(expect, (list, tuple, set)):
            expect = [expect]
        expect_msg = (
            expect_msg or 'Request status code({resp.status_code}) is not in {expect}\n{resp.text}'
        ).format(resp=resp, expect=expect)
        if resp.status_code not in expect:
            raise HarborRequestError(msg=expect_msg, resp=resp)
    return resp


def toggle_requests_debug(toggle=True):
    # These two lines enable debugging at httplib level (requests->urllib3->http.client)
    # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # The only thing missing will be the response.body which is not logged.
    level = {
        True: logging.DEBUG,
        False: logging.ERROR,
    }[toggle]
    try:
        import http.client as http_client
    except ImportError:
        # Python 2
        import httplib as http_client
    http_client.HTTPConnection.debuglevel = toggle and 1 or 0
    # You must initialize logging, otherwise you'll not see debug output.
    logging.getLogger().setLevel(level)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(level)
    requests_log.propagate = True



def gen_pw(password_length=None):
    """Default password will meet this requirement: es passwords needs at least one uppercase, downcase and 1 digit"""
    password_length = password_length or 16
    password = secrets.token_hex(password_length - 3)
    password += str(random.randint(0, 9))
    password += random.choice(string.ascii_lowercase)
    password += random.choice(string.ascii_uppercase)
    return password


class Odict:

    def __init__(self, o):
        self.__dict__.update(o)

# vim:set et sts=4 ts=4 tw=120:
