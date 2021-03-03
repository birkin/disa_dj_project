import datetime, json, logging, os, pprint, uuid

import sqlalchemy
from disa_app import models_sqlalchemy as models_alch
from disa_app import settings_app
# from disa_app.lib import person_common
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


log = logging.getLogger(__name__)


def make_session() -> sqlalchemy.orm.session.Session:
    engine = create_engine( settings_app.DB_URL, echo=True )
    Session = sessionmaker( bind=engine )
    session = Session()
    return session


class Deleter():

    def __init__( self, request_url, start_time ):
        """ Updated by manage_delete() """
        assert type(request_url) == str
        assert type(start_time) == datetime.datetime, type(start_time)
        self.session = None
        self.common = Common( request_url, start_time )
        self.grp = None
        self.prelim_status_code = None

    def validate_delete_params( self, incoming_uuid ) -> bool:
        """ Checks delete params.
            Called by views.data_reference_group(), triggered by views.edit_record() webpage. """
        log.debug( 'starting Deleter.validate_params()' )
        assert type( incoming_uuid ) == str
        validity = False
        self.session = make_session()
        try:
            grp = self.session.query( models_alch.Group ).get( incoming_uuid )
            assert type(grp) == models_alch.Group or isinstance(grp, type(None))
            validity = True
            if grp:
                self.grp = grp
                self.prelim_status_code = 200
        except:
            log.exception( 'bad params; traceback follows; processing will continue' )
        log.debug( f'validity, ``{validity}``' )
        return validity

    def manage_delete( self, user_id ) -> HttpResponse:
        """ Manages group data/api ajax 'DELETE'.
            Called by views.data_reference_group() """
        log.debug( 'starting manage_delete' )
        try:
            rfrnc = self.grp.reference
            self.session.delete( self.grp )
            self.session.commit()
            self.common.stamp_edit( user_id, rfrnc, self.session )
            resp_dct = self.prep_delete_response_data()
            resp = HttpResponse( json.dumps(resp_dct, sort_keys=True, indent=2), content_type='application/json; charset=utf-8' )
        except:
            msg = 'problem with delete, or with response-prep; see logs'
            log.exception( msg )
            resp = HttpResponse( msg, status=500 )
        return resp

    def prep_delete_response_data( self ):
        """ Prepares delete-dict data.
            Called by manage_delete() """
        log.debug( 'starting Deleter.prep_delete_response_data()' )
        return_dct = {
            'request': {
                'url': self.common.request_url,
                'method': 'DELETE',
                'payload': {},
                'timestamp': str( self.common.start_time )
            },
            'response': {
                "status": "success",
                "elapsed_time": str( datetime.datetime.now() - self.common.start_time )
            }
        }
        log.debug( f'return_dct, ``{pprint.pformat(return_dct)}``' )
        return return_dct


    ## end class Delete()






class Poster():

    def __init__( self, request_url, start_time ):
        """ Updated by manage_post() """
        assert type(request_url) == str
        assert type(start_time) == datetime.datetime, type(start_time)
        self.session = None
        self.common = Common( request_url, start_time )
        self.perceived_count = None
        self.perceived_count_estimated = None
        self.perceived_description = None
        self.perceived_reference_id = None

    def validate_post_params( self, post_dict ) -> bool:
        """ Checks post params.
            Called by views.data_reference_group(), triggered by views.edit_record() webpage 'Add Group' button save. """
        log.debug( 'starting Poster.validate_params()' )
        validity = False
        try:
            assert type(post_dict) == dict, type(post_dict)
            assert type( int(post_dict['count'][0]) ) == int
            assert type( bool(post_dict['count_estimated'][0]) ) == bool
            assert type( post_dict['description'][0] ) == str
            assert type( int(post_dict['reference_id'][0]) ) == int
            self.perceived_count = post_dict['count'][0]
            self.perceived_count_estimated = post_dict['count_estimated'][0]
            self.perceived_description = post_dict['description'][0]
            self.perceived_reference_id = post_dict['reference_id'][0]
            validity = True
        except:
            log.exception( 'bad params; traceback follows; processing will continue' )
        log.debug( f'validity, ``{validity}``' )
        return validity

    def manage_post( self, post_dict, user_id ) -> HttpResponse:
        """ Manages data/reference_group api ajax 'POST'.
            Called by views.data_reference_group(), triggered by views.edit_record() webpage 'Add Group' button save. """
        log.debug( 'starting manage_post' )
        ( count, count_estimated, description, reference_id ) = (
            int( post_dict['count'][0] ),
            bool( post_dict['count_estimated'][0] ),
            post_dict['description'][0],
            int( post_dict['reference_id'][0] )
            )
        assert ( type(count), type(count_estimated), type(description), type(reference_id) ) == ( int, bool, str, int )
        assert type(user_id) == int
        self.session = make_session()
        try:
            uid = self.execute_post_save( count, count_estimated, description, reference_id, user_id )
            assert type(uid) == str
            resp_dct = self.prep_post_response_data( uid )
            resp = HttpResponse( json.dumps(resp_dct, sort_keys=True, indent=2), content_type='application/json; charset=utf-8' )
        except:
            msg = 'problem with save, or with response-prep; see logs'
            log.exception( msg )
            resp = HttpResponse( msg, status=500 )
        log.debug( 'returning response' )
        return resp

    def execute_post_save( self, count, count_estimated, description, reference_id, user_id ) -> dict:
        """ Updates db and returns data.
            Called by manage_post() """
        log.debug( 'starting Poster.execute_save()' )
        assert ( type(count), type(count_estimated), type(description), type(reference_id), type(user_id) ) == (
            int, bool, str, int, int )
        grp = models_alch.Group()
        uid = uuid.uuid4().hex
        assert type(uid) == str
        grp.uuid = uid
        grp.count = count
        grp.count_estimated = True
        grp.description = description
        grp.reference_id = reference_id
        grp.date_created = datetime.datetime.now()
        grp.date_modified = datetime.datetime.now()
        self.session.add( grp )
        self.session.commit()  # returns None, so no way to verify success
        self.common.stamp_edit( user_id, grp.reference, self.session )
        log.debug( f'returning uuid, ``{uid}``' )
        return grp.uuid

    def prep_post_response_data( self, uid ):
        """ Prepares post-dict.
            Called by manage_posst() """
        log.debug( 'starting Poster.prep_post_response_data()' )
        assert type(uid) == str, type(uid)
        try:
            grp = self.session.query( models_alch.Group ).get( uid )
            assert type(grp) == models_alch.Group
            assert type(grp.date_created) == datetime.datetime, type(grp.date_created)
            assert type(grp.date_modified) == datetime.datetime, type(grp.date_modified)
            log.debug( f'grp.__dict__, ``{pprint.pformat(grp.__dict__)}``' )
        except:
            log.exception( f'problem querying Group on uuid, ``{uid}``; traceback follows; exception will be raised' )
            raise exception( f'unable to query just-saved Group entry' )
        response_dct = self.common.prepare_common_response_dct( grp )
        assert type(response_dct) == dict
        return_dct = {
            'request': {
                'url': self.common.request_url,
                'method': 'POST',
                'payload': {
                    'count': self.perceived_count,
                    'count_estimated': self.perceived_count_estimated,
                    'description': self.perceived_description,
                    'reference_id': self.perceived_reference_id
                    },
                'timestamp': str( self.common.start_time )
            },
            'response': response_dct
        }
        log.debug( f'return_dct, ``{pprint.pformat(return_dct)}``' )
        return return_dct

    ## end class Poster()


class Getter():

    def __init__( self, request_url, start_time ):
        """ Updated by manage_post() """
        assert type(request_url) == str
        assert type(start_time) == datetime.datetime, type(start_time)
        self.session = None
        self.common = Common( request_url, start_time )
        self.grp = None
        self.prelim_status_code = None
        self.perceived_count = None
        self.perceived_count_estimated = None
        self.perceived_description = None
        self.perceived_reference_id = None

    def validate_get_params( self, incoming_uuid ) -> bool:
        """ Checks post params.
            Called by views.data_reference_group(), triggered by views.edit_record() webpage 'Add Group' button save. """
        log.debug( 'starting Getter.validate_params()' )
        assert type( incoming_uuid ) == str
        validity = False
        self.session = make_session()
        try:
            grp = self.session.query( models_alch.Group ).get( incoming_uuid )
            assert type(grp) == models_alch.Group or isinstance(grp, type(None))
            validity = True
            if grp:
                self.grp = grp
                self.prelim_status_code = 200
        except:
            log.exception( 'bad params; traceback follows; processing will continue' )
        log.debug( f'validity, ``{validity}``' )
        return validity

    def manage_get( self ) -> HttpResponse:
        """ Manages group data/api ajax 'GET'.
            Called by views.data_reference_group(), triggered by... ? """
        log.debug( 'starting manage_get' )
        assert type(self.grp) == models_alch.Group
        resp_dict = self.prep_get_response_data()
        resp = HttpResponse( json.dumps(resp_dict, sort_keys=True, indent=2), content_type='application/json; charset=utf-8' )
        log.debug( 'returning response' )
        return resp

    def prep_get_response_data(self):
        """ Prepares get-dict data.
            Called by manage_get() """
        response_dct = self.common.prepare_common_response_dct( self.grp )
        assert type(response_dct) == dict
        return_dct = {
            'request': {
                'url': self.common.request_url,
                'method': 'GET',
                'payload': {},
                'timestamp': str( self.common.start_time )
            },
            'response': response_dct
        }
        log.debug( f'return_dct, ``{pprint.pformat(return_dct)}``' )
        return return_dct

    ## end class Getter()


class Common():
    """ Contains entrant-manager functions used by multiple method-classes. """

    def __init__( self, request_url, start_time ):
        self.request_url = request_url
        self.start_time = start_time

    def prepare_common_response_dct( self, grp ):
        """ Builds the response-dict.
            Called by prep_get_response_data() and prep_post_response_data() """
        assert type(grp) == models_alch.Group
        response_dct = {
            'group_data': {
                'uuid': grp.uuid,
                'count': grp.count,
                'count_estimated': grp.count_estimated,
                'description': grp.description,
                'date_created': str( grp.date_created ),
                'date_modified': str( grp.date_modified ),
                'reference_id': grp.reference_id,
            },
            'elapsed_time': str( datetime.datetime.now() - self.start_time )
        }
        log.debug( f'response_dct, ``{pprint.pformat(response_dct)}``' )
        return response_dct

    def stamp_edit( self, request_user_id: int, reference_obj: models_alch.Reference, session: sqlalchemy.orm.session.Session ) -> None:
        """ Updates when the Reference-object was last edited and by whom.
            Called by Updater.execute_update() and Poster.manage_post() """
        log.debug( 'starting stamp_edit()' )
        edit = models_alch.ReferenceEdit( reference_id=reference_obj.id, user_id=request_user_id, timestamp=datetime.datetime.utcnow() )
        session.add( edit )
        session.commit()
        return

    ## end class Common()
