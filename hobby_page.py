import os

import tornado.ioloop
import tornado.web
import tornado.log

from jinja2 import \
  Environment, PackageLoader, select_autoescape

PORT = int(os.environ.get('PORT', '8888'))

ENV = Environment(
  loader=PackageLoader('myapp', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

class TemplateHandler(tornado.web.RequestHandler):
  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))

class MainHandler(TemplateHandler):
  def get(self):
    self.render_template("homepage.html",{})

class MainHandler2(TemplateHandler):
  def get(self):
    self.render_template("travel.html",{})

class MainHandler3(TemplateHandler):
  def get(self):
    self.render_template("tv_shows.html",{})

class YouHandler(tornado.web.RequestHandler):
  def get(self, name):
    self.set_header("Content-Type", 'text/plain')
    self.write("Hello, {}".format(name))

class YouTooHandler(tornado.web.RequestHandler):
  def get(self):
    self.set_header("Content-Type", 'text/plain')
    name = self.get_query_argument('name', 'Nobody')
    self.write("Hello, {}".format(name))

class YouThreeHandler(tornado.web.RequestHandler):
  def get(self):
    self.set_header("Content-Type", 'text/plain')
    names = self.get_query_arguments('name')
    print(names)
    for name in names:
      self.write("Hello, {}\n".format(name))

def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/travel", MainHandler2),
    (r"/tv_shows", MainHandler3),
    (r"/hello3", YouThreeHandler),
    (r"/hello/(.*)", YouHandler),
    (
      r"/static/(.*)",
      tornado.web.StaticFileHandler,
      {'path': 'static'}
    ),
    (
      r"/images/(.*)",
      tornado.web.StaticFileHandler,
      {'path': 'images'}
    ),
  ], autoreload=True)

if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  app = make_app()
  app.listen(PORT, print('Server started on localhost:' + str(PORT)))
  tornado.ioloop.IOLoop.current().start()
