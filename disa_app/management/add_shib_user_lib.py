import json, logging, pprint


log = logging.getLogger(__name__)


user_data_structure = {
  'first_name': str,
  'last_name': str,
  'email_address': str,
  'eppn': str,
  'uuid': str,
  'old_db_id': int
}


def add( user_json_path: str ):
    is_valid: bool = validate_json( user_json_path )
    log.debug( f'is_valid, ``{is_valid}``' )
    if not is_valid:
        print( 'problem with user json-file' )
    # print( f'user_json_path, ``{user_json_path}``' )


def validate_json( user_json_path: str ) -> bool:
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
    return return_val
