__author__ = 'alejandro.cantatore'
#common utilities
import datetime as dt
from google.appengine.api import users
from types import TypeType

def format_datetime(value, format='short'):
    if format == 'short':
        format = "%d/%m/%Y"

    return dt.datetime.strftime(value, format)


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
    def isValidWeight(self,value):
        w=value
        if w:
            return float(w)
        else:
            return 0.0
    def isValidVariance(self,value):
        v=value
        if v:
            return float(v)
        else:
            return 0.0
class BiometricsValidations(Validation):
    @staticmethod
    def containsValidationType(validationType):
        return validationType in ["biometrics"]
    def isValidHeight(self,value):
        h=value
        if h:
            return int(h)
        else:
            return 0
    def isValidTarget(self,value):
        t=value
        if t:
            return float(t)
        else:
            return 0.0
#Validation Factory
class Validator(object):
    @staticmethod
    def new(validationType):
        validationClasses = [j for (i,j) in globals().iteritems() if isinstance(j, TypeType) and issubclass(j, Validation)]
        for validationClass in validationClasses :
            if validationClass.containsValidationType(validationType):
                return validationClass()
                #if research was unsuccessful, raise an error
        raise ValueError('No validation containing "%s".' % validationType)
