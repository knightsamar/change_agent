#!/usr/bin/python
import os
import sys
#print sys.path
path = '/home/sdrc/projects/change_agent'
if path not in sys.path:
        sys.path.append(path)
        sys.path.append('/home/sdrc/projects');

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
