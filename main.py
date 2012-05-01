from types import TypeType
import urllib
import datetime as dt
from datetime import timedelta
from operator import attrgetter
from webapp2_extras import routes
from webapp2_extras import json

import webapp2

from model import Entry, log_key
from model import Biometric, bio_key

from google.appengine.api import users

import jinja2
import os


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def format_datetime(value, format='short'):
    if format == 'short':
        format = "%d/%m/%Y"

    return dt.datetime.strftime(value, format)

jinja_environment.filters['datetime'] = format_datetime

'''
class MainPage(webapp2.RequestHandler):
    def createLoggedTemplates(self, bio_query, log_query, url, url_linktext):
        if bio_query.count(1) == 0 and log_query.count(1) == 0:
            template_values = {
                'bio': None,
                'entries': None,
                'url': url,
                'url_linktext': url_linktext,
                }
        elif bio_query.count(1) and log_query.count(1) > 0:
            template_values = {
                'target': self.targetStatistics(),
                'bio': bio_query.fetch(1),
                'entries': sorted(log_query.fetch(7), key=attrgetter('date')),
                'url': url,
                'url_linktext': url_linktext,
                }
        elif bio_query.count(1) == 0 and log_query.count(1) > 0:
            template_values = {
                'bio': None,
                'entries': sorted(log_query.fetch(7), key=attrgetter('date')),
                'url': url,
                'url_linktext': url_linktext,
                }
        else:
            template_values = {
                'bio': bio_query.fetch(1),
                'entries': None,
                'url': url,
                'url_linktext': url_linktext, }
        return template_values

    def targetStatistics(self):
        log_name = bio_name = (users.get_current_user().user_id())
        bio_query = Biometric.all().ancestor(bio_key(bio_name)).fetch(1)
        first_entry = Entry.all().ancestor(log_key(log_name)).order("date").fetch(1)
        last_entry = Entry.all().ancestor(log_key(log_name)).order("-date").fetch(1)

        firstday=first_entry[0].date
        lastday=last_entry[0].date
        lastweight=last_entry[0].weight
        targetweight=bio_query[0].target
        variance=last_entry[0].variance
        if lastweight and targetweight and variance > 0:
            tw=(lastweight-targetweight)*((lastday-firstday).days)/variance
            td=lastday+dt.timedelta(tw)
            target = (tw,td)
        else:
            target = None

        return target

    def createTemplate(self, currentUser, uri):
        if currentUser:
            url = users.create_logout_url(uri)
            url_linktext = 'Logout'
            log_name = bio_name = (users.get_current_user().user_id())
            bio_query = Biometric.all().ancestor(bio_key(bio_name))
            log_query = Entry.all().ancestor(log_key(log_name)).order("-date")
            bio = Biometric(parent=bio_key(bio_name))
            if not bio_query.count(1):
                bio.user = users.get_current_user()
                bio.height = 0
                bio.target = 0.00
                bio.put()

            template = jinja_environment.get_template('/template/Index.html')
            return template.render(self.createLoggedTemplates(bio_query, log_query, url, url_linktext))
        else:
            url = users.create_login_url(uri)
            url_linktext = 'Login'
            template_values = {
                'url': url,
                'url_linktext': url_linktext,
                }
            template = jinja_environment.get_template('/template/Login.html')
            return template.render(template_values)
#Entrada Principal
    def get(self):
        self.response.out.write(self.createTemplate(users.get_current_user(), self.request.uri))


class Delete(webapp2.RequestHandler):
    def post(self):
        try:
            userid = users.get_current_user().user_id()
            self.deleteRecord(self.request.get('delData'))
            self.updateBMI(userid)
            self.redirect('/?' + urllib.urlencode({'log_name': userid}))
        except ValueError:
            self.redirect('/?' + urllib.urlencode({'log_name': "Anon"}))

    def deleteRecord(self, request):
        userid = users.get_current_user().user_id()
        logDate = dt.datetime.strptime(request, "%Y-%m-%d").date()
        logQuery = Entry.all().ancestor(log_key(userid)).filter('date =', logDate)
        results = logQuery.fetch(1)
        for r in results:
            r.delete()

    def checkVariance(self,initQuery):
        a=0
        for i in initQuery:
            if a == 0:
                i.variance = 0.00
                i.put()
                a=a+1
            else:
                i.variance = initQuery[a-1].weight - i.weight
                i.put()
                a=a+1

    def updateBMI(self,userid):
        bioQuery = Biometric.all().ancestor(bio_key(userid)).filter('user =',users.get_current_user())
        initQuery = Entry.all().ancestor(log_key(userid)).order('date')
        self.checkVariance(initQuery)
        initQuery = Entry.all().ancestor(log_key(userid)).order('-date')
        if initQuery.count() > 0:
            weight = initQuery[0].weight
        if bioQuery.count() > 0:
            height = bioQuery[0].height
        if initQuery.count() and height and weight > 0:
            for b in bioQuery:
                b.bmi = float(weight) / (height/100.0)**2.0
        else:
            for b in bioQuery:
                b.bmi = 0.00
        b.put()


class Log(webapp2.RequestHandler):
    def post(self):
        try:
            userid = users.get_current_user().user_id()
            weight = self.request.get('weight')
            self.validateEntryValues(self.request.get('date'), self.request.get('weight'), userid)
            self.validateBioValues(int(self.request.get('height')), float(self.request.get('target')),weight, userid)
            self.redirect('/?' + urllib.urlencode({'log_name': userid}))
        except ValueError:
            self.redirect('/?' + urllib.urlencode({'log_name': 'Anon'}))



    def validateBioValues(self, height, target,weight, userid):
        bio = Biometric(parent=bio_key(userid))
        bioQuery = Biometric.all().ancestor(bio_key(userid))
        if  self.checkBio(height, target,weight, bioQuery) < 1:
            bio.user = users.get_current_user()
            bio.height = height
            bio.target = target
            if weight and height > 0:
                bio.bmi = float(weight) / (height/100.0)**2.0
            else:
                bio.bmi = 0.00
            bio.put()
            return True
        return False


    def validateEntryValues(self, date, weight, userid):
        entry = Entry(parent=log_key(userid))
        if date and weight:
            logDate = dt.datetime.strptime(date, "%d/%m/%Y").date()
            logWeight = float(weight)
            logQuery = Entry.all().ancestor(log_key(userid)).filter('date =', logDate)
            initQuery = Entry.all().ancestor(log_key(userid)).order('date')
            if  self.checkEntry(logWeight, logQuery) < 1:
                entry.user = users.get_current_user()
                entry.weight = logWeight
                entry.date = logDate
                entry.put()
                self.checkVariance(initQuery)
            return True
        else:
            return False

    def checkVariance(self,initQuery):
        a=0
        for i in initQuery:
            if a == 0:
                i.variance = 0.00
                a=a+1
            else:
                i.variance = initQuery[a-1].weight - i.weight
                i.put()
                a=a+1

    def checkBio(self, height, target,weight, query):
        for q in query:
            q.height = height
            q.target = target
            if weight:
                if weight:
                    if height > 0:
                        q.bmi = float(weight) / (height/100.0)**2.0
            else:
                q.bmi = 0.00
            q.put()
        return query.count(1)

    def checkEntry(self, weight, query):
        for q in query:
            q.weight = weight
            q.put()
            self.checkVariance(query)
        return query.count(1)
'''
################################################################################################
#app = webapp2.WSGIApplication([('/', MainPage), ('/log', Log), ('/delete', Delete)], debug=True)
class Validation(object):
    @staticmethod
    def containsValidationType(validationType):
        return False
    def getValidation(self):
        return 0
class EntriesValidations(Validation):
    @staticmethod
    def containsValidationType(validationType):
        return validationType in ["entries"]
    def validateWeight(self,value):
        w=value
        if w:
            return float(w)
        else:
            return 0.0
    def validateVariance(self,value):
        v=value
        if v:
            return float(v)
        else:
            return 0.0
class BiometricsValidations(Validation):
    @staticmethod
    def containsValidationType(validationType):
        return validationType in ["biometrics"]
    def validateHeight(self,value):
        h=value
        if h:
            return int(h)
        else:
            return 0
    def validateTarget(self,value):
        t=value
        if t:
            return float(t)
        else:
            return 0.0
class ValidationFactory(object):
    @staticmethod
    def newValidation(validationType):
        validationClasses = [j for (i,j) in globals().iteritems() if isinstance(j, TypeType) and issubclass(j, Validation)]
        for validationClass in validationClasses :
            if validationClass.containsValidationType(validationType):
                return validationClass()
                #if research was unsuccessful, raise an error
        raise ValueError('No validation containing "%s".' % validationType)

class Query(object):
    @staticmethod
    def containsQueryType(queryType):
        return False
    def getQuery(self):
        return 0

class BiometricsQueries(Query):
    @staticmethod
    def containsQueryType(queryType):
        return queryType in ["biometrics"]
    def getUser(self,key):
        return Biometric.all().ancestor(bio_key(key))
    def createUser(self,key):
        return Biometric(parent=bio_key(key))

class EntryQueries(Query):
    @staticmethod
    def containsQueryType(queryType):
        return queryType in ["entries"]

    def entryRsetBuilder(self,key):
        rset = Entry.all()
        rset.ancestor(log_key(key))
        return rset

    def createEntry(self,key):
        return Entry(parent=log_key(key))

    def getEntry(self,key,logDate):
        dc = DateCheck()
        date=dc.parseCurrentDate(logDate)
        rset = self.entryRsetBuilder(key)
        rset.filter('date =',date)
        return  rset

    def getEntrybyDateDesc(self,key):
        return  Entry.all().ancestor(log_key(key)).order("-date")

    def getEntryList(self,key,sd,ed):
        dc = DateCheck()
        startdate=dc.parseCurrentDate(sd)
        enddate=dc.parseCurrentDate(ed)
        rset = self.entryRsetBuilder(key)
        rset.filter('date >=',startdate)
        rset.filter('date <=',enddate)
        return  rset


class QueryFactory(object):
    @staticmethod
    def newQuery(queryType):
        queryClasses = [j for (i,j) in globals().iteritems() if isinstance(j, TypeType) and issubclass(j, Query)]
        for queryClass in queryClasses :
            if queryClass.containsQueryType(queryType):
                return queryClass()
            #if research was unsuccessful, raise an error
        raise ValueError('No query containing "%s".' % queryType)

class DateCheck():
    def parseCurrentDate(self,date):
        if date:
            y = date[0:4]
            m = date[5:7]
            d = date[8:10]
            return dt.date(int(y),int(m),int(d))
        return None

class AuthCheck():
    def checkUser(self,user):
        if user == users.get_current_user().nickname():
            return True
        return False

class RootHandler(webapp2.RequestHandler):
    """ This is the entry point class for Chompanion, handles the template construction
        get()
    """
    def get(self):
        """ This is the entry point method for Chompanion. The path is "/"
        """
        self.response.out.write(self.createTemplate(users.get_current_user(), self.request.uri))

    def createTemplate(self, currentUser, uri):
        if currentUser:
            userid=users.get_current_user().user_id()
            template = jinja_environment.get_template('/template/Log.html')
            return template.render(self.buildTemplate(userid,uri))
        else:
            url = users.create_login_url(uri)
            url_linktext = 'Login'
            template_values = {
                'url': url,
                'url_linktext': url_linktext,
                }
            template = jinja_environment.get_template('/template/Demo.html')
            return template.render(template_values)

    def buildTemplate(self,userId,uri):
        bq = QueryFactory().newQuery("biometrics").getUser(userId)
        eq = QueryFactory().newQuery("entries").getEntrybyDateDesc(userId)
        url = users.create_logout_url(uri)
        url_linktext = 'Logout'
        nick = users.get_current_user().nickname()
        if bq.count(1) == 0 and eq.count(1) == 0:
            template_values = {
                'uid':userId,
                'nick': nick,
                'bio': None,
                'entries': None,
                'url': url,
                'url_linktext': url_linktext,
                }
        elif bq.count(1) and eq.count(1) > 0:
            template_values = {
                'uid':userId,
                'target': None,#self.targetStatistics(),
                'bio': bq.fetch(1),
                'entries': sorted(eq.fetch(7), key=attrgetter('date')),
                'url': url,
                'url_linktext': url_linktext,
                }
        elif bq.count(1) == 0 and eq.count(1) > 0:
            template_values = {
                'uid':userId,
                'bio': None,
                'entries': sorted(eq.fetch(7), key=attrgetter('date')),
                'url': url,
                'url_linktext': url_linktext,
                }
        else:
            template_values = {
                'uid':userId,
                'nick':nick,
                #'date': currDate,
                'bio': bq.fetch(1),
                'entries': None,
                'url': url,
                'url_linktext': url_linktext, }
        return template_values

class UserOverviewHandler(webapp2.RequestHandler):
    """ This handles the main screen and User Bio Data updates
        get()
        put()
        post()
    """
    def get(self,user):
        """ Reads the User Data. The path is "/users/{nickname}"
        """
        if user:
            key = users.get_current_user().user_id()
            bq = QueryFactory().newQuery("biometrics").getUser(key)
            if bq.count(1) != 0:
                self.response.write(json.encode([b.to_dict() for b in bq]))

    def post(self,user):
        if user:
            height=ValidationFactory().newValidation("biometrics").validateHeight(self.request.get('height'))
            target=ValidationFactory().newValidation("biometrics").validateTarget(self.request.get('target'))
            weight=ValidationFactory().newValidation("entries").validateWeight(self.request.get('weight'))

            key = users.get_current_user().user_id()
            bq= QueryFactory().newQuery("biometrics").getUser(key)
            if bq.count(1) == 0:
                self.createUserBiometrics(QueryFactory().newQuery("biometrics").createUser(key),height,target,weight)
            else:
                self.validateUserBiometrics(bq,height,target,weight)



    def createUserBiometrics(self,ba,height,target,weight):
            self.loadBiometrics(ba,height,target,weight)

    def validateUserBiometrics(self,bq,height,target,weight):
        for b in bq:
            self.loadBiometrics(b,height,target,weight)

    def loadBiometrics(self,b,height,target,weight):
        b.user = users.get_current_user()
        b.height = height
        b.target = target
        if weight and height > 0:
            b.bmi = float(weight) / (height/100.0)**2.0
        else:
            b.bmi = 0.00
        b.put()

class EntryHandler(webapp2.RequestHandler):

    def isAuthenticated(self,user,cd):
        ac = AuthCheck()
        dc = DateCheck()
        date = dc.parseCurrentDate(cd)
        if user and date:
            if ac.checkUser(user):
                return True
        return False

    def get(self,user,cd):
        ac = AuthCheck()
        if user:
            if ac.checkUser(user):
                eq = QueryFactory().newQuery("entries").getEntry(users.get_current_user().user_id(),cd)
                if eq.count(1) != 0:
                    #JSON
                    self.response.write(json.encode([e.to_dict() for e in eq]))

    def getPostValues(self,cd):
        dc = DateCheck()
        date = dc.parseCurrentDate(cd)
        weight = ValidationFactory().newValidation("entries").validateWeight(self.request.get('weight'))
        variance =ValidationFactory().newValidation("entries").validateWeight(self.request.get('variance'))
        userid = users.get_current_user().user_id()
        return {'date':date,'weight':weight,'variance':variance,'userid':userid}

    def post(self,user,cd):
        if self.isAuthenticated(user,cd):
            values = self.getPostValues(cd)
            eq=QueryFactory().newQuery("entries").getEntry(values['userid'],cd)
            if eq.count(1) == 0:
                self.createUserEntry(QueryFactory().newQuery("entries").createEntry(values['userid']),values['weight'],values['variance'],values['date'])
            else:
                self.validateUserEntry(eq,values['weight'],values['variance'],values['date'])
        self.redirect('/users/%s/'% users.get_current_user().nickname())

    def put(self,user,cd):
        if self.isAuthenticated(user,cd):
            values = self.getPostValues(cd)
            eq = QueryFactory().newQuery("entries").getEntry(values['userid'],cd)
            if eq.count(1) == 1:
                self.validateUserEntry(eq,values['weight'],values['variance'],values['date'])
    #PAtron Factory para los queryhandlers
    def delete(self,user,cd):
        if self.isAuthenticated(user,cd):
            rset=QueryFactory().newQuery("entries").getEntry(users.get_current_user().user_id(),cd).fetch(1)
            for r in rset:
                r.delete()

    def createUserEntry(self,ea,weight,variance,date):
        self.loadEntry(ea,weight,variance,date)

    def validateUserEntry(self,eq,weight,variance,date):
        for e in eq:
            self.loadEntry(e,weight,variance,date)

    def loadEntry(self,e,weight,variance,date):
        e.user = users.get_current_user()
        e.weight = weight
        e.variance = variance
        e.date = date
        e.put()

class EntryListHandler(webapp2.RequestHandler):
    def get(self,user,sd,ed):
        ac = AuthCheck()
        if user:
            if ac.checkUser(user):
                eq = QueryFactory().newQuery("entries").getEntryList(users.get_current_user().user_id(),sd,ed)
                if eq.count(1) != 0:
                    #JSON
                    self.response.write(json.encode([e.to_dict() for e in eq]))

class DetailHandler(webapp2.RequestHandler):
    def get(self,user,date):
        print('DetailHandler')



app = webapp2.WSGIApplication([
    webapp2.Route('/', RootHandler, 'index'),
    routes.PathPrefixRoute('/users/<user:.+>',[
        webapp2.Route('/', UserOverviewHandler, 'user-overview'),
        webapp2.Route('/entry-list/<sd:.+>,<ed:.+>', EntryListHandler, 'entry-list'),
#        webapp2.Route('/entry/<cd:^(19[0-9]{2}|2[0-9]{3})(0[1-9]|1[012])([123]0|[012][1-9]|31)>', EntryHandler, 'entry'),
        webapp2.Route('/entry/<cd:.+>', EntryHandler, 'entry'),
        webapp2.Route('/entry/<date:(\d{4})-(\d{2})-(\d{2})>/detail', DetailHandler, 'detail'),
        ]),
     ])



