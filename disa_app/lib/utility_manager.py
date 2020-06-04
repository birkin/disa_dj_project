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

def prep_referents_data() -> dict:
    """ Builds referents listing.
        Called by views.utility_referents() """
    session = make_session()
    # rfrnts = session.query( models_alch.Referent ).all()
    rfrnts = session.query( models_alch.Referent ).order_by( 'id' ).all()
    log.debug( f'rfrnts, ``{pprint.pformat(rfrnts)}``' )
    rfrnts_lst = []
    for rfrnt in rfrnts:
        rfrnt_dct = {
            'db_id': rfrnt.id,
            'db_age': rfrnt.age,
            'db_sex': rfrnt.sex,
            'display_name': rfrnt.display_name()

        }
        rfrnts_lst.append( rfrnt_dct )
    data = {
        'info': 'a `referent` is a person associated with an item-record',
        'referents': rfrnts_lst
    }
    log.debug( 'returning' )
    return data




## from DISA
# @app.route('/editor/person')
# @app.route('/editor/person/<entId>')
# @login_required
# def edit_entrant(entId=None):
#     log.debug( 'starting edit_entrant' )
#     nametypes = [ { 'id': role.id, 'value': role.name, 'label': role.name }
#         for role in models.NameType.query.all()]
#     roles = [ { 'id': role.id, 'value': role.name, 'label': role.name }
#         for role in models.Role.query.all()]
#     # desc_data = models.Description.query.all()
#     origins = [ { 'id': loc.name, 'value': loc.name, 'label': loc.name }
#         for loc in models.Location.query.all()]
#     races = [ { 'id': loc.name, 'value': loc.name, 'label': loc.name }
#         for loc in models.Race.query.all()]
#     tribes = [ { 'id': loc.name, 'value': loc.name, 'label': loc.name }
#         for loc in models.Tribe.query.all()]
#     titles = [ { 'id': loc.name, 'value': loc.name, 'label': loc.name }
#         for loc in models.Title.query.all()]
#     vocations = [ { 'id': loc.name, 'value': loc.name, 'label': loc.name }
#         for loc in models.Vocation.query.all()]
#     enslavements = [ { 'id': loc.name, 'value': loc.name, 'label': loc.name }
#         for loc in models.EnslavementType.query.all()]
#     if not entId:
#         rec_id = request.args.get('rec')
#         rec = models.Reference.query.get(rec_id)
#         return render_template(
#             'entrant_edit.html', roles=roles, rec=rec, ent=None)
#     ent = models.Referent.query.get(entId)
#     return render_template(
#         'entrant_edit.html', rec=ent.reference, ent=ent,
#         nametypes=nametypes,
#         roles=roles, origins=origins, races=races, tribes=tribes,
#         vocations=vocations, enslavements=enslavements,
#         titles=titles)
