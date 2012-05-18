__author__ = 'alejandro.cantatore'
#Data Gateway Pattern implementation
import logging
from types import TypeType
from google.appengine.api import memcache
from model import Entry, log_key
from model import Biometric, bio_key
from common import *

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
        return Biometric.all().ancestor(bio_key(key)).fetch(1)
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
        return  rset.fetch(1)

    def getEntryZeroBMI(self,key):
        rset = self.entryRsetBuilder(key)
        rset.filter('bmi =',0.0)
        return  rset

    def getEntrybyDateDesc(self,key):
        return  Entry.all().ancestor(log_key(key)).order("-date")

    def getEntryList(self,key,sd,ed):
        rset = memcache.get("entry_list_%s_sd_%s_ed_%s"%(key,sd,ed))
        if rset is None:
            dc = DateCheck()
            startdate=dc.parseCurrentDate(sd)
            enddate=dc.parseCurrentDate(ed)
            rset = self.entryRsetBuilder(key)
            rset.filter('date >=',startdate)
            rset.filter('date <=',enddate)
            if not memcache.set("entry_list_%s_sd_%s_ed_%s"%(key,sd,ed),rset):
                logging.error("Error Setting Memcache")
        return  rset

    def getEntryWeek(self,key):
        rset = self.entryRsetBuilderOrderByFetchNum(key,"-date",7)
        return rset

    def getAllEntries(self,key):
        rset = self.entryRsetBuilder(key)
        rset.order("-date")
        return rset.fetch(1000)

class QueryFactory(object):
    @staticmethod
    def newQuery(queryType):
        queryClasses = [j for (i,j) in globals().iteritems() if isinstance(j, TypeType) and issubclass(j, Query)]
        for queryClass in queryClasses :
            if queryClass.containsQueryType(queryType):
                return queryClass()
                #if research was unsuccessful, raise an error
        raise ValueError('No query containing "%s".' % queryType)

