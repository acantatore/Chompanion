import urllib
import datetime as dt

import webapp2

from model import Entry, log_key
from model import Biometric, bio_key

from google.appengine.api import users

from libs.parsedatetime import parsedatetime as pdt
from libs.parsedatetime import parsedatetime_consts as pdc

import jinja2
import os


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class MainPage(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            log_name = bio_name = (users.get_current_user().user_id())
            bio_query = Biometric.all().ancestor(bio_key(bio_name))
            log_query = Entry.all().ancestor(log_key(log_name))
            if bio_query.count(1) == 0 and log_query.count(1) == 0:
                template_values = {
                    'bio': None,
                    'entries': None,
                    'url': url,
                    'url_linktext': url_linktext,
                    }
            elif bio_query.count(1) == 1 and log_query.count(1) == 0:
                template_values = {
                    'bio': bio_query.fetch(1),
                    'entries': None,
                    'url': url,
                    'url_linktext': url_linktext,
                    }
            elif bio_query.count(1) == 0 and log_query.count(1) > 1:
                template_values = {
                    'bio': None,
                    'entries': bio_query.fetch(7),
                    'url': url,
                    'url_linktext': url_linktext,
                    }
            else:
                template_values = {
                    'bio': bio_query.fetch(1),
                    'entries': log_query.fetch(7),
                    'url': url,
                    'url_linktext': url_linktext,
                    }
            template = jinja_environment.get_template('/template/Index.html')
            self.response.out.write(template.render(template_values))

        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            template_values = {
                'url': url,
                'url_linktext': url_linktext,
                }
            template = jinja_environment.get_template('/template/Login.html')
            self.response.out.write(template.render(template_values))


class Log(webapp2.RequestHandler):
    def post(self):
        try:
            userid = users.get_current_user().user_id()
            self.validateEntryValues(self.request.get('date'), self.request.get('weight'), userid)
            self.validateBioValues(int(self.request.get('height')), float(self.request.get('target')), userid)
            self.redirect('/?' + urllib.urlencode({'log_name': userid}))
        except ValueError:
            self.redirect('/?' + urllib.urlencode({'log_name': 'Anon'}))


    def validateBioValues(self, height, target, userid):
        bio = Biometric(parent=bio_key(userid))
        bioQuery = Biometric.all().ancestor(bio_key(userid))
        if  self.checkBio(height, target, bioQuery) < 1:
            bio.user = users.get_current_user()
            bio.height = height
            bio.target = target
            bio.put()
            return True
        return False


    def validateEntryValues(self, date, weight, userid):
        c = pdc.Constants()
        p = pdt.Calendar(c)
        entry = Entry(parent=log_key(userid))
        if date and weight:
            logDate = dt.datetime(p.parse(date)[0][0], p.parse(date)[0][1],
                p.parse(date)[0][2])
            logWeight = float(weight)
            logQuery = Entry.all().ancestor(log_key(userid)).filter('date =', logDate)
            if  self.checkEntry(logWeight, logQuery) < 1:
                entry.user = users.get_current_user()
                entry.weight = logWeight
                entry.date = logDate
                entry.put()
            return True
        else:
            return False

    def checkBio(self, height, target, query):
        for q in query:
            q.height = height
            q.target = target
            q.put()
        return query.count(1)

    def checkEntry(self, weight, query):
        for q in query:
            q.weight = weight
            q.put()
        return query.count(1)


app = webapp2.WSGIApplication([('/', MainPage), ('/log', Log)], debug=True)
