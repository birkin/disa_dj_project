import json, logging, pprint, sys


log = logging.getLogger(__name__)


user_data_structure = {
  'user_first_name': str,
  'user_last_name': str,
  'user_email_address': str,
  'user_eppn': str,
  'shib_conf_path': str,
  'shib_conf_backup_dir_path': str,
}


def add( user_json_path: str ):
    """ Controller for adding shib-user.
        Triggered by `$ python ./manage.py add_shib_user --user_json_path="/path/to/add_user.json" """
    is_valid: bool = validate_json( user_json_path )
    if not is_valid:
        print( 'shib user json-file check: problem; invalid' )
        sys.exit()
    else:
        print( 'shib user json-file check: good' )
    shib_backed_up = check_for_shib_backup()
    if not shib_backed_up:
        print( 'shib-backup check: problem; back up shib file' )
        sys.exit()
    else:
        print( 'shib-backup check: good' )
    if not user_added_to_shib:
        print( 'shib file check: problem; add shib user to shib file' )
        sys.exit()
    else:
        print( 'shib file check: good' )
    if not user_in_DISA_db():
        print( 'DISA-db check: shib user does not exist; will add' )
        if add_user_to_DISA_db():
            print( 'DISA-db check: shib user added' )
        else:
            print( 'DISA-db check: problem adding shib user' )
    else:
        print( 'DISA-db check: good' )
    if not user_in_django_db():
        print( 'django-db check: shib user does not exist; will add' )
        if add_user_to_django_db():
            print( 'django-db check: shib user added' )
        else:
            print( 'django-db check: problem adding shib user' )

    else:
        print( 'django-db check: good' )

    ## end def add()


def validate_json( user_json_path: str ) -> bool:
    """ Checks user-json file.
        Called by add() """
    try:
        with open( user_json_path, 'r' ) as f:
            user_info: dict = json.loads( f.read() )
            expected_keys: list = user_data_structure.keys().sorted()
            supplied_keys: list = user_info.keys().sorted()
            assert expected_keys == supplied_keys
            for ( key, val ) in user_info.items():
                expected_type = user_data_structure[key]
                supplied_type = type( user_info[key] )
                supplied_data = user_info[key]
                assert expected_type == supplied_type
                assert len( supplied_data ) > 0
            assert user_info['old_db_id'] > 0
        log.debug( 'opening and reading file was successful' )
        return_val = True
    except:
        log.exception( 'problem loading json-file; exception follows...' )
        return_val = False
    log.debug( f'return_val, ``{return_val}``' )
    return return_val

    ## end def validate_json()


def check_for_shib_backup() -> bool:
    """ Checks whether shib file has been backed up recently.
        Called by add() """
    raise Exception( 'not yet implemented' )
