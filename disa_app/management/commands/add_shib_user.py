import pathlib

from disa_app.management import add_shib_user_lib
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--shib_user_json_path')

    def handle(self, *args, **kwargs):
        if kwargs['shib_user_json_path'] == None:
            print( '`--shib_user_json_path="/path/to.json"` is required' )
        else:
            user_json_path = pathlib.Path( kwargs['shib_user_json_path'] )
            add_shib_user_lib.add( user_json_path )

