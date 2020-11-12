import pathlib

from disa_app.management import add_shib_user_lib
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--user_json_path')

    # def add_arguments(self, parser):
    #     parser.add_argument('--user-json-path',
    #         action='store',
    #         dest='user_json_path',
    #     )

    def handle(self, *args, **kwargs):
        if kwargs['user_json_path'] == None:
            print( '`--user_json_path="/path/to.json"` is required' )
        else:
            user_json_path = pathlib.Path( kwargs['user_json_path'] )
            add_shib_user_lib.add( user_json_path )

