#!/usr/bin/env python
import os
import jinja2
import webapp2

from models import Message

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("hello.html")

messages = ['Hallo!', 'Wie gehts', 'abasd', 'dasda']

class MessageboardHandler(BaseHandler):
    def get(self):
        messages = Message.query().fetch()
        return self.render_template('messageboard.html', {'messages': messages})

class SearchHandler(BaseHandler):
    def post(self):
        # frage den HTTP-Parameter 'searchtext' ab
        searchtext = self.request.get('searchtext')
        searchresults = []
        for message in messages:
            if searchtext.lower() in message.lower():
                searchresults.append(message)
        return self.render_template('search-message.html',
                 {'searchtext': searchtext, 'searchresults': searchresults})

class PostHandler(BaseHandler):
    def post(self):
        messagetext = self.request.get('messagetext')

        # speichere die message in der datenbank

        # erstelle einen neuen eintrag
        msg = Message(message_text=messagetext)

        # speichere den eintrag in der datenbank
        msg.put()

        return self.render_template('message-posted.html')

class MessageDetailsHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        return self.render_template("message_details.html", params=params)

class EditMessageHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        return self.render_template("message_edit.html", params=params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/messageboard', MessageboardHandler),
    webapp2.Route('/search-message', SearchHandler),
    webapp2.Route('/post-message', PostHandler),
    webapp2.Route('/message/<message_id:\d+>', MessageDetailsHandler),
    webapp2.Route('/message/<message_id:\d+>/edit', EditMessageHandler),
], debug=True)
