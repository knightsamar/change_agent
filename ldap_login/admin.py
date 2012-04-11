from django.contrib import admin
from ldap_login.models import *

class UsersInline(admin.TabularInline):
    model = user;
    extra = 1;

class userAdmin(admin.ModelAdmin):
    search_fields = ['username','fullname'];

class groupAdmin(admin.ModelAdmin):
	inlines = [UsersInline];

admin.site.register(group);
admin.site.register(Role);
admin.site.register(Permission);
admin.site.register(user,userAdmin);
