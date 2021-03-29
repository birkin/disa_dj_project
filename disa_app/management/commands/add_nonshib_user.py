import pathlib

from disa_app.management import add_nonshib_user_lib
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--nonshib_user_json_path')

    def handle(self, *args, **kwargs):
        if kwargs['nonshib_user_json_path'] == None:
            print( '`--nonshib_user_json_path="/path/to.json"` is required' )
        else:
            user_json_path = pathlib.Path( kwargs['nonshib_user_json_path'] )
            add_nonshib_user_lib.add( user_json_path )

