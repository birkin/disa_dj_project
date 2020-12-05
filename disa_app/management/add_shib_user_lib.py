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
            assert len
    except:
        log.exception( 'problem loading json-file; exception follows...' )
        return False
