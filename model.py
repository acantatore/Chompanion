__author__ = 'alejandro.cantatore'

from google.appengine.ext import db
from datetime import datetime
class Entry(db.Model):
    #TODO: Implementar Variancia
    """Weight Table with Variance"""
    user = db.UserProperty()
    timestamp = db.DateTimeProperty(auto_now_add=True)
    date = db.DateProperty(datetime.now().strftime("%d/%m/%Y"))
    weight = db.FloatProperty(default=0.00)
    variance = db.FloatProperty(default=0.00)
    bmi = db.FloatProperty(default=0.00)


def log_key(log_name=None):
    """Weight Table allocated per user"""
    return db.Key.from_path('log', log_name)

#TODO: Implementar Objetivos
class Biometric(db.Model):
    user = db.UserProperty()
    height = db.IntegerProperty(default=0)
    target = db.FloatProperty(default=0.00)
    bmi = db.FloatProperty(default=0.00)


def bio_key(bio_name=None):
    """Height, target & BMI rating per user"""
    return db.Key.from_path('bio', bio_name)

