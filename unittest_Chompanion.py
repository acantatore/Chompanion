__author__ = 'alejandro.cantatore'
import datetime as dt
import unittest
from main import Log
from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.api import users


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


class checkBioTest(unittest.TestCase):
    def setUp(self):
    # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()

    def tearDown(self):
        self.testbed.deactivate()

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
        self.validateBioValuesTest()
        self.validateEntryValuesTest()
        self.modelTest()



