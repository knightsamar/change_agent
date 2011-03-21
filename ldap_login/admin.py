from django.contrib import admin
from ldap_login.models import group,user

admin.site.register(group);
admin.site.register(user);


