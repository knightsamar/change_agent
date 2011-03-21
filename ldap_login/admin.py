from django.contrib import admin
from ldap_login.models import group,user

class UsersInLine(admin.TabularInline):
    model = user;
    extra = 1;

class groupAdmin(admin.ModelAdmin):
	inlines = [UsersInLine];


admin.site.register(group,groupAdmin);
admin.site.register(user);



