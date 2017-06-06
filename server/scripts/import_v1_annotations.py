DJANGO_PROJECT_DIR = '/home/ubuntu/cocotext-v2/amt/server'

import sys
import os
sys.path.append(DJANGO_PROJECT_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'server.settings'
import json
import django
import decimal
from api.models import AmtTextInstance

django.setup()


def import_v1_annotations():
    pass

if __name__ == '__main__':
    import_v1_annotations()
