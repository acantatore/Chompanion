__author__ = 'alejandro.cantatore'
import os
import unittest
from main import RootHandler
from main import EntryHandler
from main import EntryListHandler
from main import DetailHandler
from main import UserOverviewHandler
from main import AuthCheck
from main import EntryWeekHandler
from main import format_datetime
from main import BMICheck
from main import ValidationFactory,Validation,Query,QueryFactory
from main import EntryAllEntriesHandler
from model import Entry,log_key
from model import Biometric,bio_key
from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.api import users
from urllib import urlencode
import datetime as dt
import webapp2

class TestModelBio(db.Model):
    user = db.UserProperty()
    height = db.IntegerProperty()
    target = db.FloatProperty(default=0.00)
    bmi = db.FloatProperty(default=0.00)

class TestModelEntry(db.Model):
    user = db.UserProperty()
    timestamp = db.DateTimeProperty(auto_now_add=True)
    date = db.DateProperty()
    weight = db.FloatProperty(default=100.00)
    variance = db.FloatProperty(default=1.00)

class TestEntityGroupRoot(db.Model):
    """Entity group root"""
    pass

class MainTest(unittest.TestCase):
    def setUp(self):
    # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()

    def format_datetimeTest(self):
        actual = format_datetime(self.toDate(2010,10,14),format='short')
        expected = "14/10/2010"
        assert expected == actual

    def EntriesValidations_validationsTest(self):

        actual=ValidationFactory().newValidation("entries").validateWeight(None)
        expected=0.0
        self.assertEquals(actual,expected)
        actual=ValidationFactory().newValidation("entries").validateWeight(10.5)
        expected=10.5
        self.assertEquals(actual,expected)
        actual=ValidationFactory().newValidation("entries").validateVariance(None)
        expected=0.0
        self.assertEquals(actual,expected)
        actual=ValidationFactory().newValidation("entries").validateVariance(10.5)
        expected=10.5
        self.assertEquals(actual,expected)
        actual=ValidationFactory().newValidation("biometrics").validateTarget(None)
        expected=0.0
        self.assertEquals(actual,expected)
        actual=ValidationFactory().newValidation("biometrics").validateTarget(10.5)
        expected=10.5
        self.assertEquals(actual,expected)
        actual=ValidationFactory().newValidation("biometrics").validateHeight(None)
        expected=0.0
        self.assertEquals(actual,expected)
        actual=ValidationFactory().newValidation("biometrics").validateHeight(10)
        expected=10
        self.assertEquals(actual,expected)
        v=Validation()
        actual=v.getValidation()
        expected=0
        self.assertEquals(actual,expected)
        q=Query()
        actual=q.getQuery()
        expected=0
        self.assertEquals(actual,expected)
        actual=q.containsQueryType("test")
        expected=False
        self.assertEquals(actual,expected)
        self.assertRaises(ValueError,ValidationFactory().newValidation,('bio'))
        self.assertRaises(ValueError,QueryFactory().newQuery,('bio'))
    def AuthCheck_checkUserTest(self):
        ac = AuthCheck()
        actual=ac.checkUser(None)
        expected = False
        assert expected == actual, 'Current User and Requested User dont match'
        actual=ac.checkUser(users.get_current_user().nickname())
        expected = True
        assert expected == actual, 'Current User and Requested User matches'

    def RootHandler_getTest(self):
        request = webapp2.Request.blank('/')
        response = webapp2.Response()
        rh = RootHandler()
        rh.initialize(request, response)
        rh.get()
        self.setCurrentUser("adc@adc.com", "root")
        rh.get()

    def RootHandler_buildTemplateTest(self):
        request = webapp2.Request.blank('/')
        uri = request.uri
        self.setCurrentUser("adc@adc.com", "root")
        userId=users.get_current_user().user_id()
        rh = RootHandler()
        Biometric(height=100, target=75.0, parent=bio_key(userId)).put()
        rh.buildTemplate(userId,uri)
        Entry(weight=100.1, parent=log_key(userId)).put()
        rh.buildTemplate(userId,uri)
        db.delete(Biometric.all())
        rh.buildTemplate(userId,uri)

    def UserOverviewHandler_getTest(self):
        request = webapp2.Request.blank('/')
        response = webapp2.Response()
        handler = UserOverviewHandler()
        handler.initialize(request, response)
        handler.get(user=None)
        self.setCurrentUser("adc@adc.com", "aaaaaaa")
        userId=users.get_current_user().user_id()
        handler.get(user=users.get_current_user().nickname())
        Biometric(height=100, target=75.0, parent=bio_key(userId)).put()
        handler.get(user=users.get_current_user().nickname())

    def UserOverviewHandler_postTest(self):
        height = 169
        target = 75.5
        weight = 90.0
        nick= users.get_current_user().nickname()
        head = {"Content-Type" : "application/x-www-form-urlencoded", "Accept" : "text/plain"}
        payload = urlencode({"height" : int(height), "target" : float(target),"weight":float(weight)})
        #request = requests.Request("POST","/users/%s/"%nick, data=payload)
        request = webapp2.Request.blank('/users/%s/'%nick)
        request.method="POST"
        request.headers=head
        request.body=payload
        #request.query_string('height=169&weight=80&target=75')
        response = webapp2.Response()
        handler = UserOverviewHandler()
        handler.initialize(request, response)
        handler.post(user=None)
        self.setCurrentUser("adc@adc.com", "aaaaaaa")
        userId=users.get_current_user().user_id()
        db.delete(Biometric.all())
        handler.post(user=users.get_current_user().nickname())
        Biometric(height=100, target=75.0, parent=bio_key(userId)).put()
        handler.post(user=users.get_current_user().nickname())

    def UserOverviewHandler_validateUserBiometricsTest(self):
        print('validateUserBiometricsTest')
        uoh = UserOverviewHandler()
        userId=users.get_current_user().user_id()
        bq = Biometric.all().ancestor(bio_key(userId))
        weight = 80.0
        height = 169
        target = 75.0
        uoh.validateUserBiometrics(bq,height,target,weight)
        height = 0
        uoh.validateUserBiometrics(bq,height,target,weight)

    def EntryHandler_getTest(self):
        request = webapp2.Request.blank('/')
        response = webapp2.Response()
        handler = EntryHandler()
        currUser=users.get_current_user()
        nick=users.get_current_user().nickname()
        currDate=dt.date(2012, 10, 10)
        handler.initialize(request, response)
        handler.get(user=None,cd=None)
        self.setCurrentUser("adc@adc.com", "aaaaaaa")
        userId=users.get_current_user().user_id()
        handler.get(user=nick,cd='2012-10-10')
        Entry(weight=100.0, variance=5.0,date=currDate,user=currUser, parent=log_key(userId)).put()
        handler.get(user=nick,cd='2012-10-10')

    def EntryHandler_postTest(self):
        weight = 75.0
        variance = 1.4
        currDate = "2012-10-10"
        currDt =dt.date(2012, 10, 10)
        nick= users.get_current_user().nickname()
        head = {"Content-Type" : "application/x-www-form-urlencoded", "Accept" : "text/plain"}
        payload = urlencode({"date" : currDate, "variance" : float(variance),"weight":float(weight)})
        #request = requests.Request("POST","/users/%s/"%nick, data=payload)
        request = webapp2.Request.blank('/users/%s/entry/%s'%(nick,currDate))
        request.method="POST"
        request.headers=head
        request.body=payload
        currUser=users.get_current_user()
        response = webapp2.Response()
        handler = EntryHandler()
        handler.initialize(request, response)
        handler.post(user=None,cd=None)
        self.setCurrentUser("adc@adc.com", "aaaaaaa")
        userId=users.get_current_user().user_id()
        db.delete(Entry.all())
        nick=users.get_current_user().nickname()
        handler.post(user=nick,cd='2012-10-10')
        Entry(weight=100.0, variance=5.0,date=currDt,user=currUser, parent=log_key(userId)).put()
        handler.post(user=nick,cd='2012-10-10')
        db.delete(Biometric.all())
        Biometric(height=150, target=73.3, parent=bio_key(currUser.user_id())).put()
        handler.post(user=nick,cd='2012-10-10')
        #Put Test
        handler.put(user=nick,cd='2012-10-10')
        handler.put(user=nick,cd='2012-10-15')
        handler.delete(user=nick,cd='2012-10-10')

    def EntryListHandler_getTest(self):
        request = webapp2.Request.blank('/')
        response = webapp2.Response()
        currUser=users.get_current_user()

        handler = EntryListHandler()
        handler.initialize(request, response)
        handler.get(sd='2010-10-10',ed='2010-10-10',user=currUser.nickname())
        self.setCurrentUser("adc@adc.com", "aaaaaaa")
        handler.get(sd='2010-10-10',ed='2010-10-10',user=currUser.nickname())
        Entry(weight=100.0, variance=5.0,date=self.toDate(2010,10,10),user=currUser, parent=log_key(currUser.user_id())).put()
        Entry(weight=110.0, variance=5.0,date=self.toDate(2010,10,11),user=currUser, parent=log_key(currUser.user_id())).put()
        Entry(weight=115.0, variance=5.0,date=self.toDate(2010,10,12),user=currUser, parent=log_key(currUser.user_id())).put()
        handler.get(sd='2010-10-10',ed='2010-10-12',user=currUser.nickname())
    def EntryAllEntriesHandler_getTest(self):
        request = webapp2.Request.blank('/')
        response = webapp2.Response()
        currUser=users.get_current_user()
        handler = EntryAllEntriesHandler()
        handler.initialize(request, response)
        handler.get(user=currUser.nickname())
        self.setCurrentUser("adc@adc.com", "aaaaaaa")
        handler.get(user=currUser.nickname())
        Entry(weight=100.0, variance=5.0,date=self.toDate(2010,10,10),user=currUser, parent=log_key(currUser.user_id())).put()
        Entry(weight=110.0, variance=5.0,date=self.toDate(2010,10,11),user=currUser, parent=log_key(currUser.user_id())).put()
        Entry(weight=115.0, variance=5.0,date=self.toDate(2010,10,12),user=currUser, parent=log_key(currUser.user_id())).put()
        handler.get(user=currUser.nickname())

    def toDate(self,y,m,d):

        return dt.date(y,m,d)

    def EntryWeekHandler_getTest(self):
        request = webapp2.Request.blank('/')
        response = webapp2.Response()
        currUser=users.get_current_user()
        handler = EntryWeekHandler()
        handler.initialize(request, response)
        handler.get(user=currUser.nickname())
        Entry(weight=100.0, variance=5.0,date=self.toDate(2010,10,10),user=currUser, parent=log_key(currUser.user_id())).put()
        Entry(weight=110.0, variance=5.0,date=self.toDate(2010,10,11),user=currUser, parent=log_key(currUser.user_id())).put()
        Entry(weight=115.0, variance=5.0,date=self.toDate(2010,10,12),user=currUser, parent=log_key(currUser.user_id())).put()
        handler.get(user=currUser.nickname())

    def BMICheck_updateBMITest(self):
        b = BMICheck()
        currUser=users.get_current_user()
        request = webapp2.Request.blank('/')
        response = webapp2.Response()
        handler = UserOverviewHandler()
        handler.initialize(request, response)
        db.delete(Biometric.all())
        self.setCurrentUser("adc@adc.com", "aaaaaaa")
        Biometric(height=150, target=73.3, parent=bio_key(currUser.user_id())).put()
        Entry(weight=100.0,bmi=0.0, variance=5.0,date=self.toDate(2010,10,10),user=currUser, parent=log_key(currUser.user_id())).put()
        Entry(weight=110.0,bmi=0.0, variance=5.0,date=self.toDate(2010,10,11),user=currUser, parent=log_key(currUser.user_id())).put()
        Entry(weight=0.0,bmi=0.0, variance=5.0,date=self.toDate(2010,10,12),user=currUser, parent=log_key(currUser.user_id())).put()

        b.updateBMI(self,currUser.nickname())


    def EntryDetail_getTest(self):
        request = webapp2.Request.blank('/')
        response = webapp2.Response()
        handler = DetailHandler()
        handler.initialize(request, response)
        handler.get(date='2010-10-10',user=None)
        self.setCurrentUser("adc@adc.com", "aaaaaaa")
        handler.get(date='2010-10-10',user=users.get_current_user().nickname())

    def runTest(self):
        self.RootHandler_getTest()
        self.RootHandler_buildTemplateTest()
        self.UserOverviewHandler_getTest()
        self.UserOverviewHandler_postTest()
        self.UserOverviewHandler_validateUserBiometricsTest()
        self.EntryListHandler_getTest()
        self.EntryWeekHandler_getTest()
        self.EntryHandler_getTest()
        self.EntryHandler_postTest()
        self.EntryDetail_getTest()
        self.AuthCheck_checkUserTest()
        self.format_datetimeTest()
        self.EntriesValidations_validationsTest()
        self.BMICheck_updateBMITest()
        self.EntryAllEntriesHandler_getTest()

    def tearDown(self):
        self.logoutCurrentUser()
        self.testbed.deactivate()

    def setCurrentUser(self, email, user_id, is_admin=False):
        os.environ['SERVER_NAME'] = 'localhost'
        os.environ['SERVER_PORT'] = '8080'
        os.environ['AUTH_DOMAIN'] = 'example.org'
        os.environ['USER_EMAIL'] = email or ''
        os.environ['USER_ID'] = user_id or ''
        os.environ['USER_IS_ADMIN'] = '1' if is_admin else '0'

    def logoutCurrentUser(self):
        self.setCurrentUser(None, None)