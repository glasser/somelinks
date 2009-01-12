#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#


import os

import wsgiref.handlers

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util


class Link(db.Model):
  url = db.StringProperty(required=True)
  description = db.TextProperty(required=True)


class ListHandler(webapp.RequestHandler):
  def get(self):
    links = Link.all()
    path = os.path.join(os.path.dirname(__file__), 'list.html')
    self.response.out.write(template.render(path, {
        'links': Link.all(),
        'admin': users.is_current_user_admin(),
        }))


class LoginHandler(webapp.RequestHandler):
  @util.login_required
  def get(self):
    self.redirect(ListHandler.get_url())


class AddHandler(webapp.RequestHandler):
  def post(self):
    if not users.is_current_user_admin():
      self.redirect(ListHandler.get_url())
      return
    link = Link(url=self.request.get('url'),
                description=self.request.get('description'))
    link.put()
    self.redirect(ListHandler.get_url())


class DeleteHandler(webapp.RequestHandler):
  def get(self, link_id):
    if not users.is_current_user_admin():
      self.redirect(ListHandler.get_url())
      return
    link_id = long(link_id)
    link = Link.get_by_id(link_id)
    link.delete()
    self.redirect(ListHandler.get_url())


def main():
  application = webapp.WSGIApplication([
      ('/', ListHandler),
      ('/login/?', LoginHandler),
      ('/add', AddHandler),
      ('/delete/(\\d+)', DeleteHandler),
      ])
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
