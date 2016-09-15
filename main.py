import webapp2
import jinja2
import os

from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    thoughts = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):

    def get(self):
        blog = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        t = jinja_env.get_template("post-listings.html")
        response = t.render(blogs = blog)

        self.response.write(response)



class PostForm(Handler):
    def render_post_form(self, title="", thoughts="", error=""):
        self.render("post-form.html", title=title, thoughts=thoughts, error=error)

    def get(self):
        self.render_post_form()

    def post(self):
        title = self.request.get("title")
        thoughts = self.request.get("thoughts")

        if title and thoughts:
            a = Blog(title = title, thoughts = thoughts)
            a.put()

            self.redirect("/blog")

        else:
            error = "You need both a title and thoughts for a blog!"
            self.render_post_form(title, thoughts, error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        post = Blog.get_by_id(int(id))

        if post:
            response = "<h1>" + post.title + "</h1>"+ "<div>" + post.thoughts + "</div>"
            self.response.write(response)
        else:
            error="<h1>This id does not exist!</h1>"
            self.response.write(error)


app = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/blog', MainPage),
        ('/newpost', PostForm),
        webapp2.Route('/blog/<id:\d+>', ViewPostHandler)

], debug=True)
