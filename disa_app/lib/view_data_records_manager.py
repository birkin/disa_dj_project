# -*- coding: utf-8 -*-

import datetime, json, logging, operator, os, pprint

import sqlalchemy
from disa_app import settings_app
from disa_app import models_sqlalchemy as models_alch
from disa_app.lib import person_common
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound, HttpResponseRedirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


log = logging.getLogger(__name__)


# -------------
# main
# -------------

def query_record( rec_id: str ) -> dict:
    """ Handles api call for GET reference-data and associated referent-data.
        Called by views.data_records() """
    data = { 'rec': {}, 'entrants': [] }
    if rec_id == None:
        data = json.dumps( data )
        log.debug( f'no rec_id; data, ```{pprint.pformat(data)}```' )
    session = make_session()
    rec: models_sqlalchemy.Reference = session.query( models_alch.Reference ).get( rec_id )
    data['rec']['id'] = rec.id
    data['rec']['date'] = None
    if rec.date:
        data['rec']['date'] = '{}/{}/{}'.format(rec.date.month,
            rec.date.day, rec.date.year)
    data['rec']['locations'] = [ {
        'label':l.location.name,
        'value':l.location.name,
        'id': l.location.id } for l in rec.locations ]
    data['rec']['transcription'] = rec.transcription
    data['rec']['national_context'] = rec.national_context_id

    log.debug( f'rec, ``{rec}``' )
    data['rec']['image_url'] = rec.image_url

    data['rec']['record_type'] = {
        'label': rec.reference_type.name,
        'value': rec.reference_type.name,
        'id':rec.reference_type.id }

    data['entrants'] = [ {
        'name_id': ent.primary_name.id,
        'first': ent.primary_name.first,
        'last': ent.primary_name.last,
        'id': ent.id,
        'person_id': ent.person_id,
        'roles': [ role.id for role in ent.roles ] } for ent in rec.referents ]

    data['rec']['header'] = '{}'.format(
        rec.reference_type.name or '').strip()

    groups = [ {
        'uuid': rfrnc_group.uuid,
        'count': rfrnc_group.count,
        'count_estimated': rfrnc_group.count_estimated,
        'description': rfrnc_group.description,
        'date_created': str( rfrnc_group.date_created ),
        'date_modified': str( rfrnc_group.date_modified ),
        'reference_id': rfrnc_group.reference_id } for rfrnc_group in rec.groups ]
    # log.debug( f'initial-groups, ``{pprint.pformat(groups)}``' )
    sorted_groups = sorted( groups, key=lambda k: k['date_modified'], reverse=True )
    # log.debug( f'sorted-groups, ``{pprint.pformat(sorted_groups)}``' )
    data['groups'] = {
        'group_data': sorted_groups,
        'group_sort_order': 'reverse date_modified'
    }

    log.debug( f'data, ```{pprint.pformat(data)}```' )
    return data

    ## end def query_record()


def manage_reference_put( rec_id: str, payload: bytes, request_user_id: int ) -> dict:
    """ Handles api call when 'Create' button is hit in `/editor/records/?doc_id=(123)`.
        Called by views.data_records() """
    log.debug( 'starting manage_reference_put()' )

    try:

        session = make_session()
        data: dict = json.loads( payload )
        log.debug( f'data, ```{pprint.pformat(data)}```' )

        reference_type: models_sqlalchemy.ReferenceType = get_or_create_type( data['record_type'], models_alch.ReferenceType, session )

        # ref = models.Reference.query.get(refId)
        rfrnc = session.query( models_alch.Reference ).get( rec_id )

        rfrnc.locations = []
        rfrnc = process_record_locations( data['locations'], rfrnc, session )

        try:
            rfrnc.date = datetime.datetime.strptime(data['date'], '%m/%d/%Y')
        except:
            rfrnc.date = None
        rfrnc.reference_type_id = reference_type.id
        rfrnc.national_context_id = data['national_context']
        rfrnc.transcription = data['transcription']

        if 'image_url' in data.keys():
            log.debug( f'rfrnc.__dict__, ``{pprint.pformat(rfrnc.__dict__)}``' )
            log.debug( 'found `image_url` key' )
            rfrnc.image_url = data['image_url']
            log.debug( f'rfrnc.__dict__ now, ``{pprint.pformat(rfrnc.__dict__)}``' )

        session.add( rfrnc )
        session.commit()

        stamp_edit( request_user_id, rfrnc, session )

        data = { 'rec': {} }
        data['rec']['id'] = rfrnc.id
        data['rec']['date'] = ''
        if rfrnc.date:
            data['rec']['date'] = '{}/{}/{}'.format(rfrnc.date.month,
                rfrnc.date.day, rfrnc.date.year)
        data['rec']['citation'] = rfrnc.citation.id
        data['rec']['transcription'] = rfrnc.transcription
        data['rec']['national_context'] = rfrnc.national_context_id
        data['rec']['locations'] = [
            { 'label':l.location.name, 'value':l.location.name,
                'id': l.location.id } for l in rfrnc.locations ]
        data['rec']['record_type'] = {'label': rfrnc.reference_type.name,
            'value': rfrnc.reference_type.name, 'id':rfrnc.reference_type.id }

        # context =  { 'redirect': reverse( 'edit_record_url', kwargs={'rec_id': rfrnc.id} ) }
        log.debug( f'data, ```{data}```' )
    except:
        log.exception( '\n\nexception...' )
        raise Exception( 'problem; see logs' )

    return data

    ## end def manage_reference_put()


# def manage_reference_put( rec_id: str, payload: bytes, request_user_id: int ) -> dict:
#     """ Handles api call when 'Create' button is hit in `/editor/records/?doc_id=(123)`.
#         Called by views.data_records() """
#     log.debug( 'starting manage_reference_put()' )
#     session = make_session()
#     data: dict = json.loads( payload )
#     log.debug( f'data, ```{pprint.pformat(data)}```' )
#     try:  # for debugging; remove afterwards

#         reference_type: models_sqlalchemy.ReferenceType = get_or_create_type( data['record_type'], models_alch.ReferenceType, session )

#         # ref = models.Reference.query.get(refId)
#         rfrnc = session.query( models_alch.Reference ).get( rec_id )

#         rfrnc.locations = []
#         rfrnc = process_record_locations( data['locations'], rfrnc, session )

#         try:
#             rfrnc.date = datetime.datetime.strptime(data['date'], '%m/%d/%Y')
#         except:
#             rfrnc.date = None
#         rfrnc.reference_type_id = reference_type.id
#         rfrnc.national_context_id = data['national_context']
#         rfrnc.transcription = data['transcription']
#         session.add( rfrnc )
#         session.commit()

#         stamp_edit( request_user_id, rfrnc, session )

#         data = { 'rec': {} }
#         data['rec']['id'] = rfrnc.id
#         data['rec']['date'] = ''
#         if rfrnc.date:
#             data['rec']['date'] = '{}/{}/{}'.format(rfrnc.date.month,
#                 rfrnc.date.day, rfrnc.date.year)
#         data['rec']['citation'] = rfrnc.citation.id
#         data['rec']['transcription'] = rfrnc.transcription
#         data['rec']['national_context'] = rfrnc.national_context_id
#         data['rec']['locations'] = [
#             { 'label':l.location.name, 'value':l.location.name,
#                 'id': l.location.id } for l in rfrnc.locations ]
#         data['rec']['record_type'] = {'label': rfrnc.reference_type.name,
#             'value': rfrnc.reference_type.name, 'id':rfrnc.reference_type.id }

#         # context =  { 'redirect': reverse( 'edit_record_url', kwargs={'rec_id': rfrnc.id} ) }
#         log.debug( f'data, ```{data}```' )
#     except:
#         log.exception( '\n\nexception...' )
#         raise Exception( 'problem; see logs' )

#     return data

#     ## end def manage_reference_put()


def manage_post( payload: bytes, request_user_id: int ) -> dict:
    """ Handles api call when 'Create' button is hit in `/editor/records/?doc_id=(123)`.
        Called by views.data_records() """
    log.debug( 'starting manage_post()' )
    session = make_session()
    data: dict = json.loads( payload )
    log.debug( f'data, ```{pprint.pformat(data)}```' )
    try:  # for debugging; remove afterwards
        reference_type: models_sqlalchemy.ReferenceType = get_or_create_type( data['record_type'], models_alch.ReferenceType, session )

        rfrnc = models_alch.Reference()
        rfrnc.citation_id = data['citation_id']
        rfrnc.national_context_id = data['national_context']
        rfrnc.reference_type_id = reference_type.id
        session.add( rfrnc )
        session.commit()

        rfrnc.locations = []
        rfrnc = process_record_locations( data['locations'], rfrnc, session )

        try:
            rfrnc.date = datetime.datetime.strptime(data['date'], '%m/%d/%Y')
        except:
            rfrnc.date = None
        rfrnc.reference_type_id = reference_type.id
        rfrnc.national_context_id = data['national_context']
        rfrnc.transcription = data['transcription']

        if 'image_url' in data.keys():
            log.debug( f'rfrnc.__dict__, ``{pprint.pformat(rfrnc.__dict__)}``' )
            rfrnc.image_url = data['image_url']
            log.debug( f'rfrnc.__dict__ now, ``{pprint.pformat(rfrnc.__dict__)}``' )

        session.add( rfrnc )
        session.commit()

        stamp_edit( request_user_id, rfrnc, session )

        # context =  { 'redirect': reverse( 'edit_record_url', kwargs={'rec_id': rfrnc.id} ) }
        context =  { 'redirect': reverse( 'edit_record_w_recid_url', kwargs={'rec_id': rfrnc.id} ) }
        log.debug( f'context, ```{context}```' )
    except:
        log.exception( '\n\nexception...' )
        raise Exception( 'problem; see logs' )

    return context


def manage_reference_delete( rfrnc_id: str ) -> HttpResponseRedirect:  # or, much less likely, HttpResponseNotFound
    """ Handles api call when red `x` button is clicked...
        ...and then the 'Confirm delete' button is clicked in, eg, <http://127.0.0.1:8000/editor/documents/(123)/>.
        Called by views.data_reference()
        Note: this function is short enough that I could simply put this code directly into the views.data_reference()...
              ...but a good TODO would be to refactor that view and have a general views.data_record() url...
              ...handle the full CRUD set of methods -- which would all call this data_records_manager.py file """
    log.debug( 'starting manage_delete()' )
    session = make_session()
    existing = session.query( models_alch.Reference ).get( rfrnc_id )
    if existing:
        cite = existing.citation  # why did I get this?
        session.delete( existing )
        session.commit()
        # rsp = HttpResponseRedirect( redirect_url )  # if this doesn't work, i can just hit this url with requests and return the output.
    else:
        pass
    redirect_url = reverse( 'edit_citation_url', kwargs={'cite_id': cite.id} )
    log.debug( f'redirect_url, ```{redirect_url}```' )
    context =  { 'redirect': redirect_url }
    return context

# def manage_reference_delete( rfrnc_id: str ) -> HttpResponseRedirect:  # or, much less likely, HttpResponseNotFound
#     """ Handles api call when red `x` button is clicked...
#         ...and then the 'Confirm delete' button is clicked in, eg, <http://127.0.0.1:8000/editor/documents/(123)/>.
#         Called by views.data_reference()
#         Note: this function is short enough that I could simply put this code directly into the views.data_reference()...
#               ...but a good TODO would be to refactor that view and have a general views.data_record() url...
#               ...handle the full CRUD set of methods -- which would all call this data_records_manager.py file """
#     log.debug( 'starting manage_delete()' )
#     session = make_session()
#     existing = session.query( models_alch.Reference ).get( rfrnc_id )
#     if existing:
#         cite = existing.citation
#         session.delete( existing )
#         session.commit()
#         redirect_url = reverse( 'edit_citation_url', kwargs={'cite_id': cite.id} )
#         log.debug( f'redirect_url, ```{redirect_url}```' )
#         rsp = HttpResponseRedirect( redirect_url )  # if this doesn't work, i can just hit this url with requests and return the output.
#     else:
#         rsp = HttpResponseNotFound
#     log.debug( f'returning rsp, ```{rsp}```' )
#     return rsp


# -------------
# helpers
# -------------


def make_session() -> sqlalchemy.orm.session.Session:
    engine = create_engine( settings_app.DB_URL, echo=True )
    Session = sessionmaker( bind=engine )
    session = Session()
    return session


def get_or_create_type( typeData: dict, typeModel: models_alch.ReferenceType, session: sqlalchemy.orm.session.Session ) -> models_alch.ReferenceType:
    """ Gets or creates a ReferenceType instance.
        Called by manage_post() """
    log.debug( f'typeData, ```{pprint.pformat(typeData)}```' )
    if typeData['id'] == -1:
        new_type = typeModel (name=typeData['value'] )
        session.add( new_type )
        session.commit()
        log.debug( f'new_type, ```{new_type}```' )
        typ = new_type
    elif typeData == '' or typeData['id'] == 0:
        unspec = session.query( typeModel ).filter_by( name='Unspecified' ).first()
        log.debug( f'unspec, ```{unspec}```' )
        typ = unspec
    else:
        existing = session.query( typeModel ).get( typeData['id'] )
        log.debug( f'existing, ```{existing}```' )
        typ = existing
    return typ


def process_record_locations( locData: list, recObj: models_alch.Reference, session: sqlalchemy.orm.session.Session ) -> models_alch.Reference:
    """ Creates additional Location records if necessary...
        Updates ReferenceLocation records if necessary...
        Creates a linkage between the Reference record and the ReferenceLocation record if necessary.
        Called by manage_post() """
    log.debug( f'locData, ```{pprint.pformat(locData)}```' )
    locations = []
    for loc in locData:
        if loc['id'] == -1:
            location = models_alch.Location(name=loc['value'])
            session.add(location)
            session.commit()
        elif loc['id'] == 0:
            continue
        else:
            # location = models.Location.query.get(loc['id'])
            location = session.query( models_alch.Location ).get( loc['id'] )
        locations.append(location)
    # clny_state = models.LocationType.query.filter_by(name='Colony/State').first()
    clny_state = session.query( models_alch.LocationType ).filter_by( name='Colony/State' ).first()

    # city = models.LocationType.query.filter_by(name='City').first()
    city = session.query( models_alch.LocationType ).filter_by( name='City' ).first()

    # locale = models.LocationType.query.filter_by(name='Locale').first()
    locale = session.query( models_alch.LocationType ).filter_by( name='Locale' ).first()

    loc_types = [ clny_state, city, locale ]
    for loc in locations:
        rec_loc = models_alch.ReferenceLocation()
        rec_loc.reference = recObj
        rec_loc.location = loc
        idx = locations.index( loc )
        rec_loc.location_rank = idx
        if idx < len(loc_types):
            rec_loc.location_type = loc_types[idx]
        session.add(rec_loc)
    session.commit()
    log.debug( 'returning reference-instance' )
    return recObj


def stamp_edit( request_user_id: int, reference_obj: models_alch.Reference, session: sqlalchemy.orm.session.Session ) -> None:
    """ Updates when the Reference-object was last edited and by whom.
        Called by manage_post() """
    log.debug( 'starting stamp_edit()' )
    try:
        edit = models_alch.ReferenceEdit( reference_id=reference_obj.id, user_id=request_user_id, timestamp=datetime.datetime.utcnow() )
        session.add( edit )
        session.commit()
    except:
        message = 'problem updating when Reference-object was last updated and by whom'
        log.exception( f'{message}; traceback follows; processing will continue' )
    return


# -------------
# for reference
# -------------


## from DISA -- GET
# @app.route('/data/records/', methods=['GET'])
# @app.route('/data/records/<recId>', methods=['GET'])
# @login_required
# def read_record_data(recId=None):
#     data = { 'rec': {}, 'entrants': [] }
#     if recId == None:
#         return jsonify(data)
#     rec = models.Reference.query.get(recId)
#     data['rec']['id'] = rec.id
#     data['rec']['date'] = None
#     if rec.date:
#         data['rec']['date'] = '{}/{}/{}'.format(rec.date.month,
#             rec.date.day, rec.date.year)
#     data['rec']['locations'] = [
#         { 'label':l.location.name, 'value':l.location.name,
#             'id': l.location.id } for l in rec.locations ]
#     data['rec']['transcription'] = rec.transcription
#     data['rec']['national_context'] = rec.national_context_id
#     data['rec']['record_type'] = {'label': rec.reference_type.name,
#         'value': rec.reference_type.name, 'id':rec.reference_type.id }
#     data['entrants'] = [
#         {
#             'name_id': ent.primary_name.id,
#             'first': ent.primary_name.first,
#             'last': ent.primary_name.last,
#             'id': ent.id,
#             'person_id': ent.person_id,
#             'roles': [ role.id for role in ent.roles ]
#         }
#             for ent in rec.referents ]
#     data['rec']['header'] = '{}'.format(
#         rec.reference_type.name or '').strip()
#     return jsonify(data)


## from DISA -- POST/PUT
# @app.route('/data/records/', methods=['POST'])
# @app.route('/data/records/<refId>', methods=['PUT'])
# @login_required
# def update_reference_data(refId=None):
#     data = request.get_json()
#     reference_type = get_or_create_type(
#         data['record_type'], models.ReferenceType)
#     if request.method == 'POST':
#         ref = models.Reference()
#         ref.citation_id = data['citation_id']
#         ref.national_context_id = data['national_context']
#         ref.reference_type_id = reference_type.id
#         db.session.add(ref)
#         db.session.commit()
#     else:
#         ref = models.Reference.query.get(refId)
#     ref.locations = []
#     ref = process_record_locations(data['locations'], ref)
#     try:
#         ref.date = datetime.datetime.strptime(data['date'], '%m/%d/%Y')
#     except:
#         ref.date = None
#     ref.reference_type_id = reference_type.id
#     ref.national_context_id = data['national_context']
#     ref.transcription = data['transcription']
#     db.session.add(ref)
#     db.session.commit()

#     stamp_edit(current_user, ref)
#     if request.method == 'POST':
#         return jsonify(
#             { 'redirect': url_for('edit_record', recId=ref.id) })
#     data = { 'rec': {} }
#     data['rec']['id'] = ref.id
#     data['rec']['date'] = ''
#     if ref.date:
#         data['rec']['date'] = '{}/{}/{}'.format(ref.date.month,
#             ref.date.day, ref.date.year)
#     if request.method == 'POST':
#         data['entrants'] = []
#         data['rec']['header'] = '{}'.format(
#             ref.reference_type.name or '').strip()
#     data['rec']['citation'] = ref.citation.id
#     data['rec']['transcription'] = ref.transcription
#     data['rec']['national_context'] = ref.national_context_id
#     data['rec']['locations'] = [
#         { 'label':l.location.name, 'value':l.location.name,
#             'id': l.location.id } for l in ref.locations ]
#     data['rec']['record_type'] = {'label': ref.reference_type.name,
#         'value': ref.reference_type.name, 'id':ref.reference_type.id }
#     return jsonify(data)


## from DISA -- DELETE
# @app.route('/data/reference/<refId>', methods=['DELETE'])
# def delete_reference(refId):
#     existing = models.Reference.query.get(refId)
#     if existing:
#         cite = existing.citation
#         db.session.delete(existing)
#         db.session.commit()
#         return read_document_data(cite.id)
#     return redirect(url_for('editor_index'), code=404)
