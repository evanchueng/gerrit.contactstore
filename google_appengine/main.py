# Copyright 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from appsec import APPSEC
from model import ContactInfo

def _CreateApplication():
  return webapp.WSGIApplication([
    (r'^/store',  StoreContact),
    (r'^/',       GoSecure),
    (r'^/.*',     PageNotFound),
  ],
  debug=False)

class StoreContact(webapp.RequestHandler):
  def get(self):
    self.post()

  def post(self):
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    ci = ContactInfo()
    try:
      if APPSEC != self.request.get('APPSEC'):
        raise ValueError

      ci.account_id = int(self.request.get('account_id'))
      if ci.account_id < 1:
        raise ValueError

      d = self.request.get('data')
      if d is None or len(d) < 1:
        raise ValueError
      ci.data = db.Blob(d.encode('utf-8'))

      ci.email = self.request.get('email')
      if ci.email is None or len(ci.email) == 0:
        ci.email = None
        ci.domain = None
      else:
        ci.email = ci.email.lower()
        ci.domain = ci.email[ci.email.index('@') + 1:]

      f = self.request.get('filed')
      if f is None or len(f) == 0:
        f = datetime.utcnow()
      else:
        f = datetime.utcfromtimestamp(int(f))
      ci.filed = f
    except:
      self.response.set_status(500)
      self.response.out.write('BAD INPUT\n')
      raise

    try:
      ci.put()
    except:
      self.response.set_status(500)
      self.response.out.write('DATA STORE FAIL\n')
      raise

    self.response.set_status(200)
    self.response.out.write('OK\n')

class GoSecure(webapp.RequestHandler):
  def get(self):
    self.redirect('/secure/', permanent=True)

class PageNotFound(webapp.RequestHandler):
  def get(self):
    self.response.set_status(404)
    self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
    self.response.out.write("""<html>
<head>
  <title>Not Found</title>
</head>
<body>
<h1>Not Found</h1>
</html>
""")

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  application = _CreateApplication()
  main()
