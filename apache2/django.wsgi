#!/usr/bin/python
import os
import sys
#print sys.path
path = '/home/sdrc/change_agent'
if path not in sys.path:
        sys.path.append(path)
        sys.path.append('/home/sdrc');

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
