# -*- coding: utf-8 -*-

import json, os


## general

README_URL = os.environ['DISA_DJ__README_URL']

DENORMALIZED_JSON_URL = os.environ['DISA_DJ__DENORMALIZED_JSON_URL']
DENORMALIZED_JSON_PATH = os.environ['DISA_DJ__DENORMALIZED_JSON_PATH']

BROWSE_JSON_URL = os.environ['DISA_DJ__BROWSE_JSON_URL']


## db

DB_URL = os.environ['DISA_DJ__DATABASE_URL']


## auth

SUPER_USERS = json.loads( os.environ['DISA_DJ__SUPER_USERS_JSON'] )
STAFF_USERS = json.loads( os.environ['DISA_DJ__STAFF_USERS_JSON'] )  # users permitted access to admin
STAFF_GROUP = os.environ['DISA_DJ__STAFF_GROUP']  # not grouper-group; rather, name of django-admin group for permissions
TEST_META_DCT = json.loads( os.environ['DISA_DJ__TEST_META_DCT_JSON'] )
# POST_LOGIN_ADMIN_REVERSE_URL = os.environ['DISA_DJ__POST_LOGIN_ADMIN_REVERSE_URL']  # note, for a direct-view of a django-db-model, the string would be in the form of: `admin:APP-NAME_MODEL-NAME_changelist`

LOGIN_PROBLEM_EMAIL = os.environ['DISA_DJ__LOGIN_PROBLEM_EMAIL']


## basic-auth

BROWSE_USERPASS_LIST = json.loads( os.environ['DISA_DJ__BROWSE_USERPASS_JSON'] )
