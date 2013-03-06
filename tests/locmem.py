# -*- coding: utf-8 -*-
from __future__ import with_statement

from flask import current_app as app
from flask.ext.email.backends.locmem import Mail
from flask.ext.email.message import EmailMessage

from . import BaseEmailBackendTests, FlaskTestCase

class LocmemBackendTests(BaseEmailBackendTests, FlaskTestCase):
    email_backend = 'flask.ext.email.backends.locmem.Mail'

    def get_mailbox_content(self):
        return [m.message() for m in self.app.extensions['email'].outbox]

    def flush_mailbox(self):
        self.app.extensions['email'].outbox = []

    def test_locmem_shared_messages(self):
        """
        Make sure that the locmen backend populates the outbox.
        """
        connection = Mail()
        connection2 = Mail()
        email = EmailMessage('Subject', 'Content', 'bounce@example.com', ['to@example.com'], headers={'From': 'from@example.com'})
        connection.send_messages([email])
        connection2.send_messages([email])
        self.assertEqual(len(self.app.extensions['email'].outbox), 2)