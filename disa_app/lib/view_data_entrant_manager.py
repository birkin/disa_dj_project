# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint

import sqlalchemy
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


class Updater():

    def __init__( self ):
        self.session = None

    def manage_update( self, data: dict, rntId: str ) -> dict:
        """ Manages data/api ajax 'PUT'.
            Called by views.data_entrants(), triggered by views.edit_record() webpage. """
        self.session = make_session()
        rnt: models_sqlalchemy.Referent = self.session.query( models_alch.Referent ).get( rntId )
        primary_name: str = self.update_referent_name( data['name'] )


        rnt.names.append(primary_name)
        rnt.primary_name = primary_name

        1/0


        # if request.method == 'POST':
        #     prs.first_name = primary_name.first
        #     prs.last_name = primary_name.last
        #     db.session.add(prs)
        rnt.roles = [ get_or_create_referent_attribute(a, models.Role)
            for a in data['roles'] ]


        db.session.add(rnt)
        db.session.commit()

        stamp_edit(current_user, rnt.reference)

        return jsonify({
            'name_id': rnt.primary_name.id,
            'first': rnt.primary_name.first,
            'last': rnt.primary_name.last,
            'id': rnt.id,
            'person_id': rnt.person_id,
            'roles': [ role.id for role in rnt.roles ] })

    def update_referent_name( self, data: dict ) -> models_alch.ReferentName:
        """ Obtains a ReferentName object. Does not write to the db.
            Called by manage_update() """
        log.debug( f'data, ```{data}```' )
        if data['id'] == 'name':
            name = self.session.query( models_alch.ReferentName() )
            log.debug( f'name, ```{name}```' )
        else:
            name = self.session.query( models_alch.ReferentName ).get( data['id'] )
            log.debug( f'name, ```{name}```' )
        name.first = data['first']
        name.last = data['last']
        given = self.session.query( models_alch.NameType ).filter_by( name='Given' ).first()
        log.debug( f'given, ```{given}```' )
        log.debug( f'given.id, ```{given.id}```' )
        log.debug( f'type(given.id), ```{type(given.id)}```' )
        name.name_type_id = data.get('name_type', given.id)
        log.debug( 'returning name' )
        return name





## from DISA
# @app.route('/data/entrants/', methods=['POST'])
# @app.route('/data/entrants/<rntId>', methods=['PUT', 'DELETE'])
# @login_required
# def update_referent(rntId=None):
#     if request.method == 'DELETE':
#         rnt = models.Referent.query.get(rntId)
#         ref = rnt.reference
#         rels_as_sbj = models.ReferentRelationship.query.filter_by(
#             subject_id=rnt.id).all()
#         rels_as_obj = models.ReferentRelationship.query.filter_by(
#             object_id=rnt.id).all()
#         for r in rels_as_sbj:
#             db.session.delete(r)
#         for r in rels_as_obj:
#             db.session.delete(r)
#         db.session.delete(rnt)
#         db.session.commit()

#         stamp_edit(current_user, ref)

#         return jsonify( { 'id': rntId } )
#     data = request.get_json()
#     if request.method == 'POST':
#         prs = models.Person()
#         db.session.add(prs)
#         db.session.commit()
#         rnt = models.Referent(reference_id=data['record_id'])
#         rnt.person = prs
#     if request.method == 'PUT':
#         rnt = models.Referent.query.get(rntId)
#     primary_name = update_referent_name(data['name'])
#     rnt.names.append(primary_name)
#     rnt.primary_name = primary_name
#     if request.method == 'POST':
#         prs.first_name = primary_name.first
#         prs.last_name = primary_name.last
#         db.session.add(prs)
#     rnt.roles = [ get_or_create_referent_attribute(a, models.Role)
#         for a in data['roles'] ]
#     db.session.add(rnt)
#     db.session.commit()

#     stamp_edit(current_user, rnt.reference)

#     return jsonify({
#         'name_id': rnt.primary_name.id,
#         'first': rnt.primary_name.first,
#         'last': rnt.primary_name.last,
#         'id': rnt.id,
#         'person_id': rnt.person_id,
#         'roles': [ role.id for role in rnt.roles ] })
