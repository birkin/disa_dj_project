# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint

import django, sqlalchemy
from disa_app import settings_app
from disa_app import models_sqlalchemy as models_alch
from disa_app.lib import person_common
from django.conf import settings
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


def redesign_query_data( cite_id: str ) -> dict:
    """ Prepares structural form-data, and citation-data.
        Called by views.redesign_citation() """
    session = make_session()
    data = {}
    citation_type_data = build_ct_js_data( session )
    cite = session.query( models_alch.Citation ).get( cite_id )
    if cite:
        log.debug( f'cite, ``{cite}``' )
        log.debug( f'cite.references, ```{cite.references}```' )
        cite_dct = cite.dictify()
        log.debug( f'cite_dct, ``{pprint.pformat(cite_dct)}``' )
        data['ct_fields'] = citation_type_data
        data['ct_fields_json'] = json.dumps( citation_type_data )
        data['doc'] = cite_dct
        ## create json object
        cite_obj = cite_dct.copy()
        del cite_obj['references']
        cite_obj['citation_db_id'] = cite_obj.pop('id')
        cite_obj['citation_type_fields'] = cite_obj.pop('fields')
        cite_obj['citation_uuid'] = 'not-yet-implemented'
        data['citation_json'] = json.dumps( cite_obj )
        log.debug( f'data, ``{pprint.pformat(data)}``' )
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


## from DISA
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
