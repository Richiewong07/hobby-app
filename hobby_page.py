import os
import boto3

import tornado.ioloop
import tornado.web
import tornado.log

from dotenv import load_dotenv

from jinja2 import \
  Environment, PackageLoader, select_autoescape

load_dotenv('.env')

PORT = int(os.environ.get('PORT', '8888'))


ENV = Environment(
  loader=PackageLoader('myapp', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

SES_CLIENT = boto3.client(
  'ses',
  aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
  aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
  region_name="us-east-1"
)

class TemplateHandler(tornado.web.RequestHandler):
  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))

class MainHandler(TemplateHandler):
  def get(self):
    self.set_header("Content-Type", 'html')
    self.render_template("homepage.html",{})

class TravelHandler(TemplateHandler):
  def get(self):
    self.render_template("travel.html",{})

class TvShowsHandler(TemplateHandler):
  def get(self):
    self.render_template("tv_shows.html",{})

class SportsHandler(TemplateHandler):
  def get(self):
    self.render_template("sports.html",{})


class ContactHandler(TemplateHandler):
    def get(self):
        self.set_header(
          'Cache-Control',
          'no-store, no-cache, must-revalidate, max-age=0')
        self.render_template("contact.html", {})

    def post (self):
        name = self.get_body_argument('name')
        email = self.get_body_argument('email')
        subject = self.get_body_argument('subject')
        message = self.get_body_argument('message')

        response = SES_CLIENT.send_email(
          Destination={
            'ToAddresses': ['richiewong07@yahoo.com'],
          },
          Message={
            'Body': {
              'Text': {
                'Charset': 'UTF-8',
                'Data': f"{message}",
              },
            },
            'Subject': {'Charset': 'UTF-8', 'Data': f'{subject}'},
          },
          Source='richiewong07@yahoo.com',
        )
        # self.write('Thanks got your data<br>')
        # self.write('Email: ' + email)
        self.redirect('/thankyou.html')


def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/travel", TravelHandler),
    (r"/tv_shows", TvShowsHandler),
    (r"/sports", SportsHandler),
    (r"/contact", ContactHandler),
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
