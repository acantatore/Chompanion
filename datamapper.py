__author__ = 'alejandro.cantatore'
#Data Mapper Pattern: Serialization + Deserialization + Cache Handling
from types import TypeType

import logging

from google.appengine.api import memcache

from google.appengine.ext import db
from google.appengine.datastore import entity_pb
from datagateway import  *


def serialize_entities(models):
    if models is None:
        return None
    elif isinstance(models, db.Model):
        # Just one instance
        return db.model_to_protobuf(models).Encode()
    else:
    # A list
        return [db.model_to_protobuf(x).Encode() for x in models]

def deserialize_entities(data):
    if data is None:
        return None
    elif isinstance(data, str):
    # Just one instance
        return db.model_from_protobuf(entity_pb.EntityProto(data))
    else:
        return [db.model_from_protobuf(entity_pb.EntityProto(x)) for x in data]

class CachedObject(object):
    @staticmethod
    def containsCachedObjectType(cachedObjectType):
        return False
    def getCachedObject(self):
        return 0

class QueryCachedObject(CachedObject):
    @staticmethod
    def containsCachedObjectType(cachedObjectType):
        return cachedObjectType in ["query"]
    def userByKey(self,key):
        bq = deserialize_entities(memcache.get("user_%s"%key))
        if bq is None or len(bq)==0:
            bq = QueryFactory().newQuery("biometrics").getUser(key)
            if not memcache.set("user_%s"%key,serialize_entities(bq)):
                logging.error("Memcache Set Failed - Get")
        return bq

    def newUser(self,key):
        logging.debug("Creating User")
        return QueryFactory().newQuery("biometrics").createUser(key)

    def updateUser(self,b,key):
        logging.debug("Updating User")
        if b.put():
            logging.debug("User Updated")
            if not memcache.set("user_%s"%key,serialize_entities(b.all().fetch(1))):
                logging.error("Memcache user_%s"%key+" not set")
            logging.debug("Memcache set for User")

    def entryWeek(self,key):
        logging.debug("Get Entry Week by Key")
        eq = deserialize_entities(memcache.get("entry_week_%s"%key))
        if eq is None or len(eq)==0:
            eq = QueryFactory.newQuery("entries").getEntryWeek(key)
            if not memcache.set("entry_week_%s"%key,serialize_entities(eq)):
                logging.error("Error setting memcache")
        return eq

    def entryAll(self,key):
        logging.debug("Get all entries")
        eq = deserialize_entities(memcache.get("entry_all_entries_%s"%key))
        if eq is None or len(eq)==0:
            eq=QueryFactory.newQuery("entries").getAllEntries(key)
            if not memcache.set("entry_all_entries_%s"%key,serialize_entities(eq)):
                logging.error("Error Setting Memcache")
        return eq

    def entryByKeyDate(self,key,cd):
        eq = deserialize_entities(memcache.get("entry_cd%s_%s"%(cd,key)))
        if eq is None or len(eq)==0:
            eq = QueryFactory().newQuery("entries").getEntry(key,cd)
            if not memcache.set("entry_cd%s_%s"%(cd,key),serialize_entities(eq)):
                logging.error("Error Setting Memcache - get")
        return eq

    def newEntry(self,key):
        logging.debug("CreatingEntry")
        return QueryFactory().newQuery("entries").createEntry(key)

    def updateEntry(self,e,cd,key):
        logging.debug("Updating Entry")
        if e.put():
            logging.debug("Entry Updated")
            if not memcache.set("entry_cd%s_%s"%(cd,key),serialize_entities(e.all().fetch(1))):
                logging.error("Memcache Entry set failed")
            memcache.delete("entry_week_%s"%key)
            memcache.delete("entry_all_entries_%s"%key)
            logging.debug("Memcache set for Entry")

#Cache Factory
class DataMapper(object):
    @staticmethod
    def new(cachedObjectType):
        cachedObjectClasses = [j for (i,j) in globals().iteritems() if isinstance(j, TypeType) and issubclass(j, CachedObject)]
        for cachedObjectClass in cachedObjectClasses :
            if cachedObjectClass.containsCachedObjectType(cachedObjectType):
                return cachedObjectClass()
                #if research was unsuccessful, raise an error
        raise ValueError('No validation containing "%s".' % cachedObjectType)

