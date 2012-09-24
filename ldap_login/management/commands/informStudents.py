class group(models.Model):
    name = models.CharField(max_length=40,unique=True);
    created_on = models.DateTimeField(auto_now_add=True);

    def getBatch(self):
         print "====",self.name
         Three_yr_courses={ 122:'BBA-IT', 121:'BCA'} 
         Two_yr_courses={ 142:'MSc. (CA)', 141:'MBA-IT'}
         name = self.name
         if self.name.isdigit() is False:
             print "not a digit"
             all_progs = Three_yr_courses.values() + Two_yr_courses.values()
             for k in all_progs:
                if k in self.name:
                    b = self.name[self.name.index(k)+len(k):]
                    print b
                    print self.name.index(k);
                    name = self.name[self.name.index(k):self.name.index(k)+len(k)]
                    print name;
                    break;
             if name == self.name:
                print "name was blank"
                programme = self.name
                return self.name
                print "printig after returning"
             else:    
               batch = b.strip()[:7]
               programme = name

         else: 
            programme=""
            a=0
            try:
                if int(name[5:8]) in Three_yr_courses.keys():
                    a=3
                    programme=Three_yr_courses[int(name[5:8])]
                elif int(name[5:8]) in Two_yr_courses.keys():
                    a=2
                    programme=Two_yr_courses[int(name[5:8])]   
                batch = '20'+str(name[:2]) + '-' + str(a+int(name[:2])) 

            except Exception as e:
                print e;
                programme = self.name;
                batch = None;
       
         return programme,batch;

    def __str__(self):
        if self.name.isdigit() is True:
            try:
                p,b = self.getBatch();
                
                return "%s %s" %(p,b);
            except:
                return self.name
        else:
             return self.name


class user(models.Model): 
    username = models.CharField(max_length=30,primary_key=True);
    password = models.CharField(max_length=255,blank=True,null=True);
    fullname = models.CharField(max_length=255,blank=True,null=True);
    last_login = models.DateTimeField(auto_now=True);
    created_on = models.DateTimeField(auto_now_add=True);
    groups = models.ManyToManyField(group);
    allowed_viewing_feedback_about = models.ManyToManyField('manage_feedback.feedbackForm',blank=True,null=True);

    def __str__(self):
	    return self.username;
