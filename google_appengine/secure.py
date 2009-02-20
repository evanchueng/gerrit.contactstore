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

import cgi
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from model import ContactInfo

def _CreateApplication():
  return webapp.WSGIApplication([
    (r'^/secure/$',             ShowForm),
    (r'^/secure/account_id$',   QueryAccountId),
    (r'^/secure/email$',        QueryEmail),
    (r'^/secure/domain$',       QueryDomain),
    (r'^/secure/show$',         ShowData),
  ],
  debug=False)

def esc(s):
  if s is None:
    return ''
  return cgi.escape(s)

def td(out, s):
  if s is None:
    s = '&nbsp;'
  else:
    s = esc(str(s))
  out.write('<td>')
  out.write(s)
  out.write('</td>')

class ShowForm(webapp.RequestHandler):
  def get(self):
    self.response.set_status(200)
    self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
    self.response.out.write("""<html>
<head>
  <title>Query</title>
</head>
<body>
<h1>Query</h1>

<div>
  <form action="account_id" method="POST">
  <b>Account ID:</b>
  <input type="text" name="q" size="25" />
  <input type="submit" value="Search" />
  </form>
</div>

<div>
  <form action="email" method="POST">
  <b>Email Address:</b>
  <input type="text" name="q" size="25" />
  <input type="submit" value="Search" />
  </form>
</div>

<div>
  <form action="domain" method="POST">
  <b>Domain:</b>
  @<input type="text" name="q" size="25" />
  <input type="submit" value="Search" />
  </form>
</div>

</html>
""")

class QueryBase(webapp.RequestHandler):
  def post(self):
    q = self.request.get('q').lower()
    if q in ('', 'null', 'none'):
      q = None

    self.response.set_status(200)
    self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
    self.response.out.write("""<html>
<head>
  <title>Query</title>
</head>
<body>
<h1>Query '%s'</h1>
<table border="1">
<tr>
  <th>Account</th>
  <th>Email</th>
  <th>Filed</th>
  <th>Stored</th>
</tr>
""" % (esc(q)))

    found = list(self.query_for(q))
    for ci in found:
      self.response.out.write('<tr>')
      self.response.out.write('<td align="right"><a href="show?key=%s">%d</a></td>'
        % (esc(str(ci.key())), ci.account_id))
      td(self.response.out, ci.email)
      td(self.response.out, ci.filed)
      td(self.response.out, ci.stored)
      self.response.out.write('</tr>\n')

    self.response.out.write("""</table>
%d matches found.
</body>
</html>
""" % len(found))

class QueryAccountId(QueryBase):
  def query_for(self, q):
    return ContactInfo.gql(
      'WHERE account_id = :1 ORDER BY filed DESC, __key__',
      int(q)
    )

class QueryEmail(QueryBase):
  def query_for(self, q):
    return ContactInfo.gql(
      'WHERE email = :1 ORDER BY account_id, filed DESC, __key__',
      q
    )

class QueryDomain(QueryBase):
  def query_for(self, q):
    return ContactInfo.gql(
      'WHERE domain = :1 ORDER BY account_id, filed DESC, __key__',
      q
    )

class ShowData(webapp.RequestHandler):
  def get(self):
    try:
      key = db.Key(self.request.get('key'))
    except:
      self.response.set_status(404)
      self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
      self.response.out.write('Not Found\n')
      return

    ci = ContactInfo.get(key)
    if ci is None:
      self.response.set_status(404)
      self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
      self.response.out.write('Not Found\n')
    else:
      self.response.set_status(200)
      self.response.headers['Content-Type'] \
        = 'application/octet-stream'
      self.response.headers['Content-Length'] \
        = len(ci.data)
      self.response.headers['Content-Disposition'] \
        = 'inline; filename="account_%d.enc"' % ci.account_id
      self.response.out.write(ci.data)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  application = _CreateApplication()
  main()
