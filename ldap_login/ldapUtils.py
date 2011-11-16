import ldap;


class ldapManager:
    
    conn = None; #for the connection
    base_dn = 'dc=sicsr,dc=edu'; #for the Base of the Domain

    def getUsers(self,ou='10030142',attrs=['displayName','sAMAccountName','userPrincipalName']):
        '''gets all the users in the specified Organizational Unit
           by default it will retrieve the Username (samaccountname in M$ terms) AND the name of the person
           
           it will return a list of dictionaries (one per user) with attributes as the keys of the dictionaries.
        '''
        print ou
        self.connect();
        filters = '(objectclass=person)';
        where = 'OU=%s,%s' % (ou,self.base_dn);
        
        raw_result = self.conn.search_s(where,ldap.SCOPE_SUBTREE,filters,attrs);
        result = []
        for r in raw_result:
            result.append(r[1]); #r[1] is the dictionary of attrs for that user
        
        return result;

    def connect(self,server='10.10.21.2',username='moodleldap@sicsr.edu',password='m00dl3',):
        '''connects to the given ldap server using name and password.
            this user must preferably have permissions of traversal, browsing if not everything
        '''
        self.conn = ldap.initialize('ldap://%s' % server);
        self.conn.simple_bind_s(username,password);

        #this is necessary due to the weird implementation of LDAPv3 in M$AD:
        #refer: http://www.python-ldap.org/faq.shtml
        self.conn.set_option(ldap.OPT_REFERRALS,0)
        
    def getGroups(self):
        '''
        gets all the groups in the AD

        returns a list of all group names which can be used for OU-based searching
        '''
        self.connect();
        filters = '(objectCategory=organizationalUnit)'; #see http://tools.ietf.org/html/rfc4515.html for the syntax
        attrs = ['name']
        where = self.base_dn;
        raw_result = self.conn.search_s(where,ldap.SCOPE_SUBTREE,filters,attrs);
        result = []
        #now is a bit tricky, because we need to extract exact OU Names for usage.
        for r in raw_result:
            if r[0] is None: #I don't know WHY but it is listing such elements!
                continue;
            else:
                d = r[1];
                name = d['name']
                actual_name = name[0]
                result.append(actual_name)
        return result;

def demo():
    l = ldapManager();
    groups = l.getGroups();
    print groups;

    for g in groups:
          print "Members of %s " % g;    
          print l.getUsers(g);
