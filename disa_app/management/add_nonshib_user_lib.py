"""
add() is the manager function, triggered by:
`$ python ./manage.py add_nonshib_user --user_json_path="/path/to/add_user.json"`
"""

import json, logging, pathlib, pprint, sys
from uuid import UUID

import sqlalchemy
import sqlalchemy.orm
from disa_app import models_sqlalchemy as models_alch
from disa_app import settings_app


log = logging.getLogger(__name__)


user_data_structure = {
  'nonshib_user_first_name': str,
  'nonshib_user_last_name': str,
  'nonshib_user_email_address': str,
  'nonshib_user_uuid': str
}


class UserInfo():

    def __init__( self ):
        self.supplied_email_address = ''
        self.supplied_data_valid = False

    ## end class UserInfo()


def add( user_json_path ):
    """ Controller for adding shib-user.
        Triggered by `$ python ./manage.py add_nonshib_user --user_json_path="/path/to/add_user.json"` """
    assert type( user_json_path ) == pathlib.PosixPath
    print( '\n-------\n=> starting nonshib user add' )
    user_info = UserInfo()
    user_json_path_str = str( user_json_path ); assert type( user_json_path_str ) == str
    is_valid = validate_json( user_json_path_str, user_info ); assert type( is_valid ) == bool
    if not is_valid:
        print( '=> nonshib user json-file check: problem; invalid' )
        sys.exit()
    else:
        print( '=> nonshib user json-file check: good' )
    if not user_in_DISA_db( user_info.supplied_email_address ):
        print( '=> DISA-db check: nonshib user does not exist; will add' )
        if add_user_to_DISA_db():
            print( '=> DISA-db check: nonshib user added' )
        else:
            print( '=> DISA-db check: problem adding nonshib user' )
    else:
        print( '=> DISA-db check: good' )
    if not user_in_django_db():
        print( 'django-db check: nonshib user does not exist; will add' )
        if add_user_to_django_db():
            print( 'django-db check: nonshib user added' )
        else:
            print( 'django-db check: problem adding nonshib user' )

    else:
        print( 'django-db check: good' )

    ## end def add()


def validate_json( user_json_path, user_info ) -> bool:
    """ Checks user-json file.
        Called by add() """
    assert type(user_json_path) == str, type(user_json_path)
    assert repr( type(user_info) ) == "<class 'disa_app.management.add_nonshib_user_lib.UserInfo'>"
    try:
        with open( user_json_path, 'r' ) as f:
            supplied_user_info = json.loads( f.read() ); assert type(supplied_user_info) == dict
            expected_keys = sorted( list(user_data_structure.keys()) )
            supplied_keys = sorted( list(supplied_user_info.keys()) )
            assert expected_keys == supplied_keys
            for ( key, val ) in supplied_user_info.items():
                expected_type = user_data_structure[key]
                supplied_type = type( supplied_user_info[key] )
                supplied_data = supplied_user_info[key]
                assert expected_type == supplied_type
                assert len( supplied_data ) > 0
            UUID( supplied_user_info['nonshib_user_uuid'], version=4 )  # raises Exception on failure
        log.debug( 'opening and reading file was successful' )
        user_info.supplied_email_address = supplied_user_info['nonshib_user_email_address']
        user_info.supplied_uuid = supplied_user_info['nonshib_user_uuid']
        return_val = True
    except:
        log.exception( 'problem loading json-file; exception follows...' )
        return_val = False
    log.debug( f'return_val, ``{return_val}``' )
    return return_val

    ## end def validate_json()


def user_in_DISA_db( email_address ):
    """ Checks to see if user has been added to the DISA.db.
        Called by add() """
    assert type( email_address ) == str
    return_val = False
    sqlalch_session = make_sqlalch_session()
    assert repr( type(sqlalch_session) ) == "<class 'sqlalchemy.orm.session.Session'>"
    log.debug( 'about to query User' )
    user_obj = sqlalch_session.query( models_alch.User ).filter_by( email=email_address ).first()
    log.debug( f'user_obj, ``{user_obj}``' )
    if user_obj:
        return_val = True
    sqlalch_session.close()
    log.debug( f'return_val, ``{return_val}``' )
    return return_val


def make_sqlalch_session() -> sqlalchemy.orm.session.Session:
    """ Sets up sqlalchemy session.
        Called by user_in_DISA_db(). """
    engine = sqlalchemy.create_engine( settings_app.DB_URL, echo=False )
    Session = sqlalchemy.orm.sessionmaker( bind=engine )
    session = Session()
    assert repr( type(session) ) == "<class 'sqlalchemy.orm.session.Session'>"
    log.debug( 'returning session' )
    return session


def add_user_to_DISA_db():
    1/0
