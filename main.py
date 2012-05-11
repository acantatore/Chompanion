from types import TypeType
from decimal import *
import urllib,hashlib
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

    def entryRsetBuilderOrderByFetchNum(self,key,orderby,rows):
        rset = Entry.all()
        rset.ancestor(log_key(key))
        rset.order(orderby)
        return rset.fetch(rows)


    def createEntry(self,key):
        return Entry(parent=log_key(key))

    def getEntry(self,key,logDate):
        dc = DateCheck()
        date=dc.parseCurrentDate(logDate)
        rset = self.entryRsetBuilder(key)
        rset.filter('date =',date)
        return  rset

    def getEntryZeroBMI(self,key):
        rset = self.entryRsetBuilder(key)
        rset.filter('bmi =',0.0)
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

    def getEntryWeek(self,key):
        rset = self.entryRsetBuilderOrderByFetchNum(key,"-date",7)
        return rset

    def getAllEntries(self,key):
        rset = self.entryRsetBuilder(key)
        rset.order("-date")
        return rset

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

class BMICheck(object):
    @staticmethod
    def updateBMI(self,user):
        ac = AuthCheck()
        if ac.checkUser(user):
            key = users.get_current_user().user_id()
            eq=QueryFactory().newQuery("entries").getEntryZeroBMI(key)
            bq= QueryFactory().newQuery("biometrics").getUser(key)
            if eq.count(1) > 0 and bq[0].height > 0:
                height = bq[0].height
                for e in eq:
                    weight = e.weight
                    if weight > 0:
                        e.bmi = round(float(weight) / (height/100.0)**2.0,2)
                        e.put()
                    else:
                        e.bmi = 0.00
                        e.put()


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
            template = jinja_environment.get_template('/template/Login.html')
            return template.render(template_values)

    def buildTemplate(self,userId,uri):
        bq = QueryFactory().newQuery("biometrics").getUser(userId)
        eq = QueryFactory().newQuery("entries").getEntrybyDateDesc(userId)
        url = users.create_logout_url(uri)
        url_linktext = 'Logout'
        nick = users.get_current_user().nickname()
        # Set your variables here
        email = users.get_current_user().email()

        size = 40

        # construct the url
        gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d':'retro', 's':str(size)})
        template_values = {
            'uid':userId,
            'nick': nick,
            'gurl': gravatar_url,
            'url': url,
            'url_linktext': url_linktext,
            }

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
            BMICheck.updateBMI(self,user)
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
            bmi=Decimal((weight) / (height/100.0)**2.0).quantize(Decimal('.01'),rounding=ROUND_UP)
            b.bmi = float(bmi)
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
            bq= QueryFactory().newQuery("biometrics").getUser(values['userid'])
            if eq.count(1) == 0:
                self.createUserEntry(QueryFactory().newQuery("entries").createEntry(values['userid']),values['weight'],values['variance'],values['date'], bq[0].height)
            else:
                self.validateUserEntry(eq,values['weight'],values['variance'],values['date'], bq[0].height)

        self.redirect('/users/%s/'% users.get_current_user().nickname())



    def put(self,user,cd):
        if self.isAuthenticated(user,cd):
            values = self.getPostValues(cd)
            eq = QueryFactory().newQuery("entries").getEntry(values['userid'],cd)
            bq= QueryFactory().newQuery("biometrics").getUser(values['userid'])
            if eq.count(1) == 1:
                self.validateUserEntry(eq,values['weight'],values['variance'],values['date'],bq[0].height)
    #PAtron Factory para los queryhandlers
    def delete(self,user,cd):
        if self.isAuthenticated(user,cd):
            rset=QueryFactory().newQuery("entries").getEntry(users.get_current_user().user_id(),cd).fetch(1)
            for r in rset:
                r.delete()

    def createUserEntry(self,ea,weight,variance,date,height):
        self.loadEntry(ea,weight,variance,date,height)

    def validateUserEntry(self,eq,weight,variance,date,height):
        for e in eq:
            self.loadEntry(e,weight,variance,date,height)

    def loadEntry(self,e,weight,variance,date,height):
        e.user = users.get_current_user()
        e.weight = weight
        if weight and height > 0:
            bmi=Decimal((weight) / (height/100.0)**2.0).quantize(Decimal('.01'),rounding=ROUND_UP)
            e.bmi = float(bmi)
        else:
            e.bmi = 0.00
        e.variance = variance
        e.date = date
        e.put()

class EntryListHandler(webapp2.RequestHandler):
    def get(self,user,sd,ed):
        ac = AuthCheck()
        if user and ac.checkUser(user):
                self.response.write(
                    jsonBuilder.encodeResponse(
                        QueryFactory().newQuery("entries").getEntryList(users.get_current_user().user_id(),sd,ed)
                    )
                )


class EntryWeekHandler(webapp2.RequestHandler):
    def get(self,user):
        ac = AuthCheck()
        if user and ac.checkUser(user):
                self.response.write(
                    jsonBuilder.encodeResponse(
                        QueryFactory.newQuery("entries").getEntryWeek(users.get_current_user().user_id())
                    )
                )
class EntryAllEntriesHandler(webapp2.RequestHandler):
    def get(self,user):
        ac = AuthCheck()
        if user and ac.checkUser(user):
            self.response.write(
                jsonBuilder.encodeResponse(
                QueryFactory.newQuery("entries").getAllEntries(users.get_current_user().user_id())
            )
            )

class DetailHandler(webapp2.RequestHandler):
    def get(self,user,date):
        print('DetailHandler')

class jsonBuilder(object):
    @staticmethod
    def encodeResponse(eq):
        if eq:
            #JSON
            return json.encode([e.to_dict() for e in eq])

app = webapp2.WSGIApplication([
    webapp2.Route('/', RootHandler, 'index'),
    routes.PathPrefixRoute('/users/<user:.+>',[
        webapp2.Route('/', UserOverviewHandler, 'user-overview'),
        webapp2.Route('/entry-list/<sd:.+>,<ed:.+>', EntryListHandler, 'entry-list'),
        webapp2.Route('/entry-week', EntryWeekHandler, 'entry-week'),
        webapp2.Route('/entry/<cd:.+>', EntryHandler, 'entry'),
        webapp2.Route('/entry/<date:(\d{4})-(\d{2})-(\d{2})>/detail', DetailHandler, 'detail'),
        webapp2.Route('/entries', EntryAllEntriesHandler, 'entry-all')
        ]),
     ])



