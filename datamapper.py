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
        bq = memcache.get("user_%s"%key)

        if bq is None or len(bq)==0:
            bq = QueryFactory().newQuery("biometrics").getUser(key)
            if not memcache.set("user_%s"%key,bq):
                logging.error("Memcache Set Failed - Get")
        return bq

    def newUser(self,key):
        logging.debug("Creating User")
        return QueryFactory().newQuery("biometrics").createUser(key)

    def updateUser(self,b):
        logging.debug("Updating User")
        if b.put():
            logging.debug("User Updated")
            if not memcache.set("user_%s"%b.user,b):
                logging.error("Memcache user_%s"%b.user+" not set")
            logging.debug("Memcache set for User")

    def entryByKeyDate(self,key,cd):
        eq = memcache.get("entry_cd%s_%s"%(cd,key))
        if eq is None:
            eq = QueryFactory().newQuery("entries").getEntry(key,cd)
            if not memcache.add("entry_cd%s_%s"%(cd,key),eq):
                logging.error("Error Setting Memcache - get")
        return eq


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

