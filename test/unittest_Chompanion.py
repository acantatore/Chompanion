__author__ = 'alejandro.cantatore'
import os
import datetime as dt
import unittest
from main import MainPage
from main import Log
from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.api import users
import webapp2


class TestModelBio(db.Model):
    user = db.UserProperty()
    height = db.IntegerProperty()
    target = db.FloatProperty(default=0.00)
    bmi = db.FloatProperty(default=0.00)


class TestModelEntry(db.Model):
    user = db.UserProperty()
    timestamp = db.DateTimeProperty(auto_now_add=True)
    date = db.DateTimeProperty()
    weight = db.FloatProperty(default=100.00)
    variance = db.FloatProperty(default=1.00)


class TestEntityGroupRoot(db.Model):
    """Entity group root"""
    pass

class modelTest(unittest.TestCase):
    def setUp(self):
    # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()
        self.setCurrentUser("adc@adc.com","aaaaaaa")

    def tearDown(self):
        self.logoutCurrentUser()
        self.testbed.deactivate()

    def setCurrentUser(self,email, user_id, is_admin=False):
        os.environ['SERVER_NAME'] = 'localhost'
        os.environ['SERVER_PORT'] = '8080'
        os.environ['AUTH_DOMAIN'] = 'example.org'
        os.environ['USER_EMAIL'] = email or ''
        os.environ['USER_ID'] = user_id or ''
        os.environ['USER_IS_ADMIN'] = '1' if is_admin else '0'

    def logoutCurrentUser(self):
        self.setCurrentUser(None, None)

    def modelTest(self):
        cut = Log()
        root = TestEntityGroupRoot(key_name="root")
        queryEmpty = TestModelBio.all().ancestor(root.key())
        actual = cut.checkBio(100, 100.0, queryEmpty)
        expected = 0
        assert expected == actual, 'ErrorBio'
        queryEmpty = TestModelEntry.all().ancestor(root.key())
        actual = cut.checkEntry(100.0, queryEmpty)
        expected = 0
        assert expected == actual, 'ErrorEntry'

        TestModelBio(height=100, target=75.0, parent=root.key()).put()
        queryFull = TestModelBio.all().ancestor(root.key())
        actual = cut.checkBio(100, 100.0, queryFull)
        expected = 1
        assert expected == actual, 'ok'
        TestModelEntry(weight=100.1, parent=root.key()).put()
        queryFull = TestModelEntry.all().ancestor(root.key())
        actual = cut.checkEntry(100.0, queryFull)
        expected = 1
        assert expected == actual, 'ok'

    def runTest(self):


        self.modelTest()

class mainTest(unittest.TestCase):
    def createTemplateTest(self):
        request = webapp2.Request.blank('/')
        url = users.create_logout_url(request.uri)
        url_linktext = 'Logout'
        cut = MainPage()
        cut.createTemplate(users.get_current_user(),request.uri)
        cut.createTemplate(None,request.uri)

    def validateMainTest(self):
        request = webapp2.Request.blank('/')
        response = webapp2.Response()
        handler = Log()
        handler.initialize(request, response)
        handler.post()
        self.assertEqual(response.status, "302 Moved Temporarily")

    def createLoggedTemplatesTest(self):
        request = webapp2.Request.blank('/')
        url = users.create_logout_url(request.uri)
        url_linktext = 'Logout'
        cut = MainPage()
        root = TestEntityGroupRoot(key_name="root")

        queryBio = TestModelBio.all().ancestor(root.key())
        queryLog = TestModelEntry.all().ancestor(root.key())
        #Bio=0 Entry=0
        cut.createLoggedTemplates(queryBio,queryLog,url,url_linktext)
        TestModelBio(height=100, target=75.0, parent=root.key()).put()
        #Bio=1 Entry=0
        cut.createLoggedTemplates(queryBio,queryLog,url,url_linktext)
        TestModelEntry(weight=100.1, parent=root.key()).put()
        #Bio=1 Entry=1
        cut.createLoggedTemplates(queryBio,queryLog,url,url_linktext)
        db.delete(TestModelBio.all())
        #Bio=0 Entry=1
        cut.createLoggedTemplates(queryBio,queryLog,url,url_linktext)

    def runTest(self):
        self.validateMainTest()
        self.createLoggedTemplatesTest()
        self.createTemplateTest()

    def setUp(self):
    # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()
        self.setCurrentUser("adc@adc.com","aaaaaaa")

    def tearDown(self):
        self.logoutCurrentUser()
        self.testbed.deactivate()

    def setCurrentUser(self,email, user_id, is_admin=False):
        os.environ['SERVER_NAME'] = 'localhost'
        os.environ['SERVER_PORT'] = '8080'
        os.environ['AUTH_DOMAIN'] = 'example.org'
        os.environ['USER_EMAIL'] = email or ''
        os.environ['USER_ID'] = user_id or ''
        os.environ['USER_IS_ADMIN'] = '1' if is_admin else '0'

    def logoutCurrentUser(self):
        self.setCurrentUser(None, None)

class logTest(unittest.TestCase):

    def validateLogTest(self):
        request = webapp2.Request.blank('/')
        response = webapp2.Response()
        handler = MainPage()
        handler.initialize(request, response)
        handler.get()
        self.assertEqual(response.status, "200 OK")


    def validateEntryValuesTest(self):
        cut = Log()
        date = dt.datetime
        mockUser = users.User("test@test", "gmail.com", "AAA")
        actual = cut.validateEntryValues(str(date.now()), 100, mockUser.user_id())
        expected = True
        assert expected == actual, 'ok'
        actual = cut.validateEntryValues(str(date.now()), None, mockUser.user_id())
        expected = False
        assert expected == actual, 'error'

    def validateBioValuesTest(self):
        cut = Log()
        mockUser = users.User("test@test", "gmail.com", "AAA")
        actual = cut.validateBioValues(100, 100.1, mockUser.user_id())
        expected = True
        assert expected == actual, 'ok'
        actual = cut.validateBioValues(100, None, mockUser.user_id())
        expected = False
        assert expected == actual, 'error'

    def runTest(self):

        self.validateBioValuesTest()
        self.validateEntryValuesTest()
        self.validateLogTest()



    def setUp(self):
# First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()
        self.setCurrentUser("adc@adc.com","aaaaaaa")

    def tearDown(self):
        self.logoutCurrentUser()
        self.testbed.deactivate()

    def setCurrentUser(self,email, user_id, is_admin=False):
        os.environ['SERVER_NAME'] = 'localhost'
        os.environ['SERVER_PORT'] = '8080'
        os.environ['AUTH_DOMAIN'] = 'example.org'
        os.environ['USER_EMAIL'] = email or ''
        os.environ['USER_ID'] = user_id or ''
        os.environ['USER_IS_ADMIN'] = '1' if is_admin else '0'

    def logoutCurrentUser(self):
        self.setCurrentUser(None, None)

