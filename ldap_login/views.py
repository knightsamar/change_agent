# Create your views here.
import ldap
from django_auth_ldap.config import LDAPSearch
#ldap_login
def login(request):
    AUTH_LDAP_SERVER_URI = "172.17.2.12"
    AUTH_LDAP_BIND_DN = ""
    AUTH_LDAP_BIND_PASSWORD = ""
    AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=example,dc=com", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

    AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=example,dc=com"
	#try ldap login
		#If cannot locate ldap server,
			#try local login
		#else
			#do ldap login


	#if successful ldap login
		#update last_login
		#store encrypted password
		#start session

	#unsuccessful ldap login
		#wrong username/password!!!
			
