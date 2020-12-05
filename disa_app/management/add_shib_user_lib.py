import json, logging, pprint


log = logging.getLogger(__name__)


def add( user_json_path: str ):
    is_valid: bool = validate_json( user_json_path )
    log.debug( f'is_valid, ``{is_valid}``' )
    print( f'user_json_path, ``{user_json_path}``' )


def validate_json( user_json_path: str ) -> bool:
    try:
        with open( user_json_path, 'r' ) as f:
            user_info: dict = json.loads( f.read() )
            for field in [ 'first_name', 'last_name', 'email_address', 'eppn', 'uuid' ]:
                assert len( user_info[field] ) > 0
            assert user_info['old_db_id'] > 0
        log.debug( 'opening and reading file was successful' )
        return_val = True
    except:
        log.exception( 'problem loading json-file; exception follows...' )
        return_val = False
    return return_val
