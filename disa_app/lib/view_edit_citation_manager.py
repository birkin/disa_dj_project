# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint

import django, sqlalchemy
from disa_app import settings_app
from disa_app import models_sqlalchemy as models_alch
from disa_app.lib import person_common
from django.conf import settings
from django.core.urlresolvers import reverse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


log = logging.getLogger(__name__)


def make_session() -> sqlalchemy.orm.session.Session:
    engine = create_engine( settings_app.DB_URL, echo=True )
    Session = sessionmaker( bind=engine )
    session = Session()
    return session


def query_data( cite_id: str ) -> dict:
    """ Queries and massages data.
        Called by views.edit_citation() """
    session = make_session()
    data = {}
    citation_type_data = build_ct_js_data( session )
    cite = session.query( models_alch.Citation ).get( cite_id )
    if cite:
        log.debug( f'cite, ``{cite}``' )
        log.debug( f'cite.references, ```{cite.references}```' )
        cite_dct = cite.dictify()
        data['ct_fields'] = citation_type_data
        data['ct_fields_json'] = json.dumps( citation_type_data )
        data['doc'] = cite_dct
    else:
        data = None
    log.debug( f'data, ```{data}```' )
    return data


# def redesign_query_data( cite_id: str ) -> dict:
#     """ Prepares structural form-data, and citation-data.
#         Called by views.redesign_citation() """
#     session = make_session()
#     data = {}
#     citation_type_data = build_ct_js_data( session )
#     cite = session.query( models_alch.Citation ).get( cite_id )
#     if cite:
#         log.debug( f'cite, ``{cite}``' )
#         log.debug( f'cite.references, ```{cite.references}```' )
#         cite_dct = cite.dictify()
#         log.debug( f'cite_dct, ``{pprint.pformat(cite_dct)}``' )
#         data['ct_fields'] = citation_type_data
#         data['ct_fields_json'] = json.dumps( citation_type_data )
#         data['doc'] = cite_dct
#         ## create json object
#         cite_obj = cite_dct.copy()
#         del cite_obj['references']
#         cite_obj['citation_db_id'] = cite_obj.pop('id')
#         cite_obj['citation_type_fields'] = cite_obj.pop('fields')
#         cite_obj['citation_uuid'] = 'not-yet-implemented'
#         data['citation_json'] = json.dumps( cite_obj )
#         log.debug( f'data, ``{pprint.pformat(data)}``' )
#         ## new-user-template
#         data['new_user_template'] = prep_new_user_payload_template()
#         # data['data_itemrecord_api_url'] = reverse( 'data_record_url' )
#     else:
#         data = None
#     log.debug( f'data, ```{data}```' )
#     return data


def redesign_query_data( cite_id: str, scheme, host ) -> dict:
    """ Prepares structural form-data, and citation-data.
        Called by views.redesign_citation() """
    log.debug( 'starting redesign_query_data()' )
    log.debug( f'cite_id, ``{cite_id}``' )
    assert type(cite_id) == str; assert type(scheme) == str; assert type(host) == str
    session = make_session()
    data = {}
    citation_type_data = build_ct_js_data( session )
    cite = session.query( models_alch.Citation ).get( cite_id )
    user_api_info = prep_user_api_info( scheme, host ); assert type(user_api_info) == dict
    if cite:
        log.debug( f'cite, ``{cite}``' )
        log.debug( f'cite.references, ```{cite.references}```' )
        cite_dct = cite.dictify()
        log.debug( f'cite_dct, ``{pprint.pformat(cite_dct)}``' )
        data['ct_fields'] = citation_type_data
        # data['ct_fields_json'] = json.dumps( citation_type_data )
        data['doc'] = cite_dct
        ## create json object
        cite_obj = cite_dct.copy()
        del cite_obj['references']
        cite_obj['citation_db_id'] = cite_obj.pop('id')
        cite_obj['citation_type_fields'] = cite_obj.pop('fields')
        cite_obj['citation_uuid'] = 'not-yet-implemented'
        # data['citation_json'] = json.dumps( cite_obj )
        log.debug( f'data, ``{pprint.pformat(data)}``' )
        ## new-user-template
        data['new_user_template'] = prep_new_user_payload_template()
        data['user_api_info'] = user_api_info
        data['data_itemrecord_api_url_root'] = '%s://%s%s' % ( scheme, host, reverse('data_record_url') )
        data['API_URL_ROOT'] = '%s://%s%s' % ( scheme, host, reverse('data_root_url') )
        log.debug( f'api-url-root, ``{data["API_URL_ROOT"]}``' )
    else:
        data = None
    log.debug( f'data, ```{data}```' )
    return data


def manage_create( user_id: int ) -> dict:
    """ Creates new document.
        Called by views.edit_citation() """
    session = make_session()
    data = {}
    citation_type_data = build_ct_js_data( session )
    data['ct_fields'] = citation_type_data
    data['ct_fields_json'] = json.dumps( citation_type_data )
    data['doc']: {}
    log.debug( f'data, ```{data}```' )
    return data


# ----------
# helpers
# ----------


def prep_new_user_payload_template() -> dict:
    """ Adds new-user sample-payload to context.
        DEPRECATED!
        Called by redesign_query_data() """

    new_user_template = {
        'post_api_url': reverse( 'data_referent_url', kwargs={'rfrnt_id': 'new'} ),
        'sample_payload': {
            'age': 0,
            'id': 'new',
            'names': [
              {'id': 'name', 'first': '(sample)John', 'last': '(sample)Doe', 'name_type': 'Given'}
            ],
            'origins': [],
            'races': [],
            'sex': '',
            'titles': [{ 'id': '', 'label': '', 'value': '' }],
            'tribes': [],
            'vocations': [{'id': '', 'label': '', 'value': ''}],
            'record_id': '(sample)49',
            'roles': [
                {'id': '(sample)3', 'name': '(sample)Priest'}
            ]
        }
      }   
    return new_user_template

def prep_user_api_info( scheme, host ) -> dict:
    """ Adds user-api info to context.
        Called by redesign_query_data() """
    assert type(scheme) == str; assert type(host) == str
    create_user_info = {
        'api_url': '%s://%s%s' % (
            scheme,
            host,
            reverse('data_referent_url', kwargs={'rfrnt_id': 'new'}) ),
        'api_method': 'POST',
        'sample_payload': {
            'id': 'new',
            'name': {'first': '', 'id': 'name', 'last': ''},
            'record_id': '',
            'roles': [
                {'id': '', 'name': ''},
            ]
        }
    }
    get_user_info = {
        'api_url': '%s://%s%s' % (
            scheme,
            host,
            reverse('data_referent_url', kwargs={'rfrnt_id': 'THE-REFERENT-ID'}) ),
        'api_method': 'GET',
        'sample_payload': None
    }
    update_user_info_SIMPLE = {
        'api_url': '%s://%s%s' % (
            scheme,
            host,
            reverse('data_referent_url', kwargs={'rfrnt_id': 'THE-REFERENT-ID'}) ),
        'api_method': 'PUT',
        'sample_payload': {
            'id': 'THE-REFERENT-ID',
            'name': {'first': '', 'id': 'name', 'last': ''},
            'record_id': '',
            'roles': [
                {'id': '', 'name': ''},
            ]
        }
    }
    update_user_info_DETAILS = {
        'api_url': '%s://%s%s' % (
            scheme,
            host,
            reverse( 'data_entrants_details_url', kwargs={'rfrnt_id': 'THE-REFERENT-ID'} ) ),
        'api_method': 'PUT',
        'sample_payload': {
            'names': [],
            'age': '',
            'sex': '',
            'races': [],
            'tribes': [],
            'origins': [],
            'statuses': [],
            'titles': [],
            'vocations': []
        }
    }
    delete_user_info = {
        'api_url': '%s://%s%s' % (
            scheme,
            host,
            reverse('data_referent_url', kwargs={'rfrnt_id': 'THE-REFERENT-ID'}) ),
        'api_method': 'DELETE',
        'sample_payload': None
    }
    user_api_info = {
        'create_user_info': create_user_info,
        'get_user_info': get_user_info,
        'update_user_info_SIMPLE': update_user_info_SIMPLE,
        'update_user_info_DETAILS': update_user_info_DETAILS,
        'delete_user_info': delete_user_info }
    log.debug( f'user_api_info, ``{pprint.pformat(user_api_info)}``' )
    return user_api_info

    ## end prep_user_api_info()


def build_ct_js_data( session ) -> dict:
    """ Builds structural data for the page's javascript.
        Called by query_data()
        TODO: I don't understand the purpose of the 'rank' data; log that and grok it. """
    included = [ 'Book', 'Book Section', 'Document', 'Interview', 'Journal Article', 'Magazine Article', 'Manuscript', 'Newspaper Article', 'Thesis', 'Webpage' ]

    # ct = models.CitationType.query.filter( models.CitationType.name.in_(included) ).all()
    ct = session.query( models_alch.CitationType ).filter( models_alch.CitationType.name.in_(included) ).all()

    ct_fields = {
        c.id: [ {   'name': f.zotero_field.name,
                    'rank': f.rank,
                    'display': f.zotero_field.display_name }
            for f in c.zotero_type.template_fields ]
                for c in ct }

    add_pages_field = ['Document', 'Book', 'Thesis', 'Manuscript']
    for c in ct:
        if c.name in add_pages_field:
            pages = { 'name': 'pages', 'display':'Pages' }
            fields = ct_fields[c.id]
            date = [ f for f in fields if f['name'] == 'date'][0]
            pages['rank'] = date['rank'] + 1
            for f in fields:
                if f['rank'] > date['rank']:
                    f['rank'] += 1
            ct_fields[c.id].append(pages)

    log.debug( f'ct_fields, ```{ct_fields}```' )
    return ct_fields


## =========
## from DISA
## =========
# @app.route('/editor/documents/<citeId>')
# @login_required
# def edit_citation(citeId=None):
#     log.debug( 'starting edit_citation' )
#     included = [ 'Book', 'Book Section', 'Document', 'Interview',
#         'Journal Article', 'Magazine Article', 'Manuscript',
#         'Newspaper Article', 'Thesis', 'Webpage' ]
#     ct = models.CitationType.query.filter(
#         models.CitationType.name.in_(included)).all()
#     ct_fields = {
#         c.id: [ {   'name': f.zotero_field.name,
#                     'rank': f.rank,
#                     'display': f.zotero_field.display_name }
#             for f in c.zotero_type.template_fields ]
#                 for c in ct }
#     add_pages_field = ['Document', 'Book', 'Thesis', 'Manuscript']
#     for c in ct:
#         if c.name in add_pages_field:
#             pages = { 'name': 'pages', 'display':'Pages' }
#             fields = ct_fields[c.id]
#             date = [ f for f in fields if f['name'] == 'date'][0]
#             pages['rank'] = date['rank'] + 1
#             for f in fields:
#                 if f['rank'] > date['rank']:
#                     f['rank'] += 1
#             ct_fields[c.id].append(pages)
#     if not citeId:
#         return render_template('document_edit.html',
#             doc=None, ct_fields=ct_fields )
#     cite = models.Citation.query.get(citeId)
#     # citation_data = { f.field.name: f.field_data for f in cite.citation_data }
#     return render_template('document_edit.html',
#         doc=cite, ct_fields=ct_fields )
