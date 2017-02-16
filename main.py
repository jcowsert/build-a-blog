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
import webapp2
import jinja2
import cgi
import os

from google.appengine.ext import db

#setup jinja2
curr_dir = os.path.dirname(__file__)
template_dir = os.path.join(curr_dir, 'templates')

file_system_loader = jinja2.FileSystemLoader(template_dir)
jinja_env = jinja2.Environment(loader=file_system_loader)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    title= db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainPage(Handler):
    def get(self):
        self.redirect('/blog')



class Blog(Handler):
    def get(self):
        blogs = db.GqlQuery("Select * from BlogPost order By created desc limit 5")
        self.render("front.html", blogs=blogs)

class NewPost(Handler):

    def render_front(self, title ="", content="", error=""):
        self.render("newpost.html", title=title, content=content, error=error)

    def get(self):
        self.render_front()


    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            b = BlogPost(title = title, content = content)
            b.put()
            blog_id = b.key().id()
            self.redirect('/blog/%s' % blog_id)
        else:
            error = "we need both a title and content"
            self.render_front(title, content, error)

class ViewPostHandler(Handler):
    def get(self, id):
        if BlogPost.get_by_id(int(id)) == None:
            error = "No Post associated id"
            self.response.write(error)
        else:

            blog_id = BlogPost.get_by_id(int(id))
            self.render("post.html", blog_id= blog_id )




app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', Blog),
    ('/blog/NewPost', NewPost),
    webapp2.Route(r'/blog/<id:\d+>', ViewPostHandler)
], debug=True)
