from decimal import *
import logging
import urllib,hashlib
from webapp2_extras import routes
from webapp2_extras import json
import webapp2

from google.appengine.api import users
from google.appengine.api import memcache
import jinja2
import os

from common import format_datetime as format_datetime
from common import DateCheck,AuthCheck,Validator;

from datamapper import *

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

jinja_environment.filters['datetime'] = format_datetime


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

    def createTemplate(self,currentUser, uri):
        if currentUser:
            userid=users.get_current_user().user_id()
            template = jinja_environment.get_template('/template/Log.html')
            return template.render(self.buildTemplate(userid,uri))
        else:
            template_values = memcache.get("template")
            if template_values is not None:
                return template_values
            else:
                url = users.create_login_url(uri)
                url_linktext = 'Login'
                template_values = {
                    'url': url,
                    'url_linktext': url_linktext,
                    }
                if not memcache.add("template",template_values):
                    logging.error("Memcache set failed")
                template = jinja_environment.get_template('/template/Login.html')
                return template.render(template_values)

    def buildTemplate(self,userId,uri):
        template_values = memcache.get("template_%s"%userId)
        if template_values is not None:
            return template_values
        else:
            bq = DataMapper().new("query").userByKey(userId)

            if len(bq) == 0:
                UserOverviewHandler.loadBiometrics(QueryFactory().newQuery("biometrics").createUser(userId),None,None,None)
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
            if not memcache.add("template_%s"%userId,template_values):
                logging.error("Memcache set failed.")
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
            #BMICheck.updateBMI(self,user)
            bq = DataMapper().new("query").userByKey(key)
            if len(bq) != 0:
                self.response.write(json.encode([b.to_dict() for b in bq]))

    def post(self,user):
        if user:
            height=Validator().new("biometrics").isValidHeight(self.request.get('height'))
            target=Validator().new("biometrics").isValidTarget(self.request.get('target'))
            weight=Validator().new("entries").isValidWeight(self.request.get('weight'))
            key = users.get_current_user().user_id()
            bq = DataMapper().new("query").userByKey(key)
            if len(bq) == 0:
                self.createUserBiometrics(DataMapper().new("query").newUser(key),height,target,weight)
            else:
                self.validateUserBiometrics(bq,height,target,weight)

    def createUserBiometrics(self,ba,height,target,weight):
        self.loadBiometrics(ba,height,target,weight)

    def validateUserBiometrics(self,bq,height,target,weight):
        for b in bq:
            self.loadBiometrics(b,height,target,weight)

    @staticmethod
    def loadBiometrics(b,height,target,weight):
        b.user = users.get_current_user()
        if height>0:
            b.height = height
        if target>0:
            b.target = target
        if weight and height > 0:
            bmi=Decimal((weight) / (height/100.0)**2.0).quantize(Decimal('.01'),rounding=ROUND_UP)
            b.bmi = float(bmi)
        else:
            b.bmi = 0.00
        DataMapper().new("query").updateUser(b, users.get_current_user().user_id())

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
                key =users.get_current_user().user_id()
                eq=DataMapper().new("query").entryByKeyDate(key,cd)
                if eq.count(1) != 0:
                    self.response.write(json.encode([e.to_dict() for e in eq]))

    def getPostValues(self,cd):
        dc = DateCheck()
        date = dc.parseCurrentDate(cd)
        weight = Validator().new("entries").isValidWeight(self.request.get('weight'))
        variance =Validator().new("entries").isValidWeight(self.request.get('variance'))
        userid = users.get_current_user().user_id()
        return {'date':date,'weight':weight,'variance':variance,'userid':userid}

    def post(self,user,cd):
        if self.isAuthenticated(user,cd):
            values = self.getPostValues(cd)
            key = values['userid']
            eq=DataMapper().new("query").entryByKeyDate(key,cd)
            bq = DataMapper().new("query").userByKey(key)
            if eq.count(1) == 0:
                self.createUserEntry(QueryFactory().newQuery("entries").createEntry(values['userid']),values['weight'],values['variance'],values['date'], bq[0].height)
            else:
                self.validateUserEntry(eq,values['weight'],values['variance'],values['date'], bq[0].height)

        self.redirect('/users/%s/'% users.get_current_user().nickname())



    def put(self,user,cd):
        if self.isAuthenticated(user,cd):
            values = self.getPostValues(cd)
            key = values['userid']
            eq=DataMapper().new("query").entryByKeyDate(key,cd)
            bq = DataMapper().new("query").userByKey(key)
            if eq.count(1) == 1:
                self.validateUserEntry(eq,values['weight'],values['variance'],values['date'],bq[0].height)


    def delete(self,user,cd):
        if self.isAuthenticated(user,cd):
            rset=QueryFactory().newQuery("entries").getEntry(users.get_current_user().user_id(),cd).fetch(1)
            for r in rset:
                r.delete()

    def createUserEntry(self,ea,weight,variance,date,height):
        self.loadEntry(ea,weight,variance,date,height)
        if not memcache.add("entry_cd%s_%s"%(date,users.get_current_user().user_id()),ea):
            logging.error("Error Setting Memcache - get")
    def validateUserEntry(self,eq,weight,variance,date,height):
        for e in eq:
            self.loadEntry(e,weight,variance,date,height)
        if not memcache.set("entry_cd%s_%s"%(date,users.get_current_user().user_id()),eq):
            logging.error("Error Setting Memcache - get")

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



