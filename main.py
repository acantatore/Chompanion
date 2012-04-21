import urllib
import datetime as dt

from operator import attrgetter
import webapp2

from model import Entry, log_key
from model import Biometric, bio_key

from google.appengine.api import users

import jinja2
import os


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def format_datetime(value, format='short'):
    if format == 'short':
        format = "%d/%m/%Y"

    return dt.datetime.strftime(value, format)

jinja_environment.filters['datetime'] = format_datetime


class MainPage(webapp2.RequestHandler):
    def createLoggedTemplates(self, bio_query, log_query, url, url_linktext):
        if bio_query.count(1) == 0 and log_query.count(1) == 0:
            template_values = {
                'bio': None,
                'entries': None,
                'url': url,
                'url_linktext': url_linktext,
                }
        elif bio_query.count(1) and log_query.count(1) > 0:
            template_values = {
                'bio': bio_query.fetch(1),
                'entries': sorted(log_query.fetch(7), key=attrgetter('date')),
                'url': url,
                'url_linktext': url_linktext,
                }
        elif bio_query.count(1) == 0 and log_query.count(1) > 0:
            template_values = {
                'bio': None,
                'entries': sorted(log_query.fetch(7), key=attrgetter('date')),
                'url': url,
                'url_linktext': url_linktext,
                }
        else:
            template_values = {
                'bio': bio_query.fetch(1),
                'entries': None,
                'url': url,
                'url_linktext': url_linktext, }
        return template_values

    def createTemplate(self, currentUser, uri):
        if currentUser:
            url = users.create_logout_url(uri)
            url_linktext = 'Logout'
            log_name = bio_name = (users.get_current_user().user_id())
            bio_query = Biometric.all().ancestor(bio_key(bio_name))
            log_query = Entry.all().ancestor(log_key(log_name)).order("-date")
            bio = Biometric(parent=bio_key(bio_name))
            if not bio_query.count(1):
                bio.user = users.get_current_user()
                bio.height = 0
                bio.target = 0.00
                bio.put()

            template = jinja_environment.get_template('/template/Index.html')
            return template.render(self.createLoggedTemplates(bio_query, log_query, url, url_linktext))
        else:
            url = users.create_login_url(uri)
            url_linktext = 'Login'
            template_values = {
                'url': url,
                'url_linktext': url_linktext,
                }
            template = jinja_environment.get_template('/template/Login.html')
            return template.render(template_values)

    def get(self):
        self.response.out.write(self.createTemplate(users.get_current_user(), self.request.uri))


class Delete(webapp2.RequestHandler):
    def post(self):
        try:
            userid = users.get_current_user().user_id()
            self.deleteRecord(self.request.get('delData'))
            self.updateBMI(userid)
            self.redirect('/?' + urllib.urlencode({'log_name': userid}))
        except ValueError:
            self.redirect('/?' + urllib.urlencode({'log_name': "Anon"}))


    def deleteRecord(self, request):
        userid = users.get_current_user().user_id()
        logDate = dt.datetime.strptime(request, "%Y-%m-%d").date()
        logQuery = Entry.all().ancestor(log_key(userid)).filter('date =', logDate)
        results = logQuery.fetch(1)
        for r in results:
            r.delete()

    def checkVariance(self,initQuery):
        a=0
        for i in initQuery:
            if a == 0:
                i.variance = 0.00
                i.put()
                a=a+1
            else:
                i.variance = initQuery[a-1].weight - i.weight
                i.put()
                a=a+1

    def updateBMI(self,userid):
        bioQuery = Biometric.all().ancestor(bio_key(userid)).filter('user =',users.get_current_user())
        initQuery = Entry.all().ancestor(log_key(userid)).order('date')
        self.checkVariance(initQuery)
        initQuery = Entry.all().ancestor(log_key(userid)).order('-date')
        if initQuery.count() > 0:
            weight = initQuery[0].weight
        if bioQuery.count() > 0:
            height = bioQuery[0].height
        if initQuery.count() and height and weight > 0:
            for b in bioQuery:
                b.bmi = float(weight) / (height/100.0)**2.0
        else:
            for b in bioQuery:
                b.bmi = 0.00
        b.put()


class Log(webapp2.RequestHandler):
    def post(self):
        try:
            userid = users.get_current_user().user_id()
            weight = self.request.get('weight')
            self.validateEntryValues(self.request.get('date'), self.request.get('weight'), userid)
            self.validateBioValues(int(self.request.get('height')), float(self.request.get('target')),weight, userid)
            self.redirect('/?' + urllib.urlencode({'log_name': userid}))
        except ValueError:
            self.redirect('/?' + urllib.urlencode({'log_name': 'Anon'}))



    def validateBioValues(self, height, target,weight, userid):
        bio = Biometric(parent=bio_key(userid))
        bioQuery = Biometric.all().ancestor(bio_key(userid))
        if  self.checkBio(height, target,weight, bioQuery) < 1:
            bio.user = users.get_current_user()
            bio.height = height
            bio.target = target
            if weight and height > 0:
                bio.bmi = float(weight) / (height/100.0)**2.0
            else:
                bio.bmi = 0.00
            bio.put()
            return True
        return False


    def validateEntryValues(self, date, weight, userid):
        entry = Entry(parent=log_key(userid))
        if date and weight:
            logDate = dt.datetime.strptime(date, "%d/%m/%Y").date()
            logWeight = float(weight)
            logQuery = Entry.all().ancestor(log_key(userid)).filter('date =', logDate)
            initQuery = Entry.all().ancestor(log_key(userid)).order('date')
            if  self.checkEntry(logWeight, logQuery) < 1:
                entry.user = users.get_current_user()
                entry.weight = logWeight
                entry.date = logDate
                entry.put()
                self.checkVariance(initQuery)
            return True
        else:
            return False

    def checkVariance(self,initQuery):
        a=0
        for i in initQuery:
            if a == 0:
                i.variance = 0.00
                a=a+1
            else:
                i.variance = initQuery[a-1].weight - i.weight
                i.put()
                a=a+1

    def checkBio(self, height, target,weight, query):
        for q in query:
            q.height = height
            q.target = target
            if weight:
                if weight:
                    if height > 0:
                        q.bmi = float(weight) / (height/100.0)**2.0
            else:
                q.bmi = 0.00
            q.put()
        return query.count(1)

    def checkEntry(self, weight, query):
        for q in query:
            q.weight = weight
            q.put()
            self.checkVariance(query)
        return query.count(1)


app = webapp2.WSGIApplication([('/', MainPage), ('/log', Log), ('/delete', Delete)], debug=True)

