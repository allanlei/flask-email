# from __future__ import with_statement

# from ..message import Message
# from ..signals import email_dispatched

# from .base import BaseMail

# import requests



# class Connection(object):
#     def __enter__(self):
#         return self

#     def __exit__(self, exc_type, exc_value, tb):
#         pass

#     def send(self, message):
#         if message.date is None:
#             message.date = time.time()
#         if not message.send_to:
#             return

#         # from_email = sanitize_address(email_message.from_email, email_message.encoding)
#         # recipients = [sanitize_address(addr, email_message.encoding) for addr in email_message.recipients()]

#         try:
#             requests.post("https://api.mailgun.net/v2/{mailgun_domain}/messages".format(mailgun_domain=self.mailgun_domain),
#                 auth=("api", self.mailgun_access_key),
#                 files=MultiDict([('attachment', attachment) for attachment in message.attachments]),
#                 data={
#                     'from': message.sender,
#                     'to': message.send_to,
#                     # 'cc':
#                     # 'bcc': 
#                     'subject': "Hello",
#                     'text': "Testing some Mailgun awesomness!",
#                     # 'html': ''
#                 }
#             )
#         except:
#             if not self.fail_silently:
#                 raise

#         if r.status_code != requests.OK:
#             if not self.fail_silently:
#                 raise Exception(r)

#         if email_dispatched:
#             email_dispatched.send(message, app=self.app)


# class Mail(BaseMail):
#     def init_app(self, app):
#         self.mailgun_domain = app.config.get('MAILGUN_DOMAIN')
#         # self.mailgun_api_url = app.config.get('MAILGUN_API_URL')
#         self.mailgun_access_key = app.config.get('MAILGUN_ACCESS_KEY')
#         super(Mail, self).init_app(app)

#     def send_message(self, *args, **kwargs):
#         self.send(Message(*args, **kwargs))

#     def connect(self):
#         """
#         Opens a connection to the mail host.

#         :param max_emails: the maximum number of emails that can
#                            be sent in a single connection. If this
#                            number is exceeded the Connection instance
#                            will reconnect to the mail server. The
#                            DEFAULT_MAX_EMAILS config setting is used
#                            if this is None.
#         """
#         return Connection(self)