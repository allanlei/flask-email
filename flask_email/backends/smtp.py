"""SMTP email backend class."""
import smtplib
import socket
import threading

from ..utils import DNS_NAME
from ..message import sanitize_address
from ..encoding import force_bytes
from ..signals import email_dispatched

from .base import BaseMail


class Mail(BaseMail):
    """
    A wrapper that manages the SMTP network connection.
    """
    def init_app(self, app, host=None, port=None, username=None, password=None,
                 use_tls=None, use_ssl=None, **kwargs):
        """
        Initializes your mail settings from the application
        settings.

        You can use this if you want to set up your Mail instance
        at configuration time.

        :param app: Flask application instance
        """
        super(Mail, self).init_app(app, **kwargs)
        self.host = host or app.config.get('MAIL_HOST') or app.config.get('MAIL_SERVER')
        self.port = int(port or app.config.get('MAIL_PORT', 25))
        if username is None:
            self.username = app.config.get('MAIL_USERNAME')
        else:
            self.username = username
        if password is None:
            self.password = app.config.get('MAIL_PASSWORD')
        else:
            self.password = password
        if use_tls is None:
            self.use_tls = app.config.get('MAIL_USE_TLS', False)
        else:
            self.use_tls = use_tls
        if use_ssl is None:
            self.use_ssl = app.config.get('MAIL_USE_SSL', False)
        else:
            self.use_ssl = use_ssl
        self.connection = None
        self._lock = threading.RLock()

    def open(self):
        """
        Ensures we have a connection to the email server. Returns whether or
        not a new connection was required (True or False).
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return False
        try:
            # If local_hostname is not specified, socket.getfqdn() gets used.
            # For performance, we use the cached FQDN for local_hostname.
            if self.use_ssl:
                self.connection = smtplib.SMTP_SSL(self.host, self.port,
                                           local_hostname=DNS_NAME.get_fqdn())
            else:
                self.connection = smtplib.SMTP(self.host, self.port,
                                           local_hostname=DNS_NAME.get_fqdn())

            self.connection.set_debuglevel(int(self.debug))

            if self.use_tls:
                self.connection.ehlo()
                self.connection.starttls()
                self.connection.ehlo()
            if self.username and self.password:
                self.connection.login(self.username, self.password)

            return True
        except:
            if not self.fail_silently:
                raise

    def close(self):
        """Closes the connection to the email server."""
        try:
            try:
                self.connection.quit()
            except socket.sslerror:
                # This happens when calling quit() on a TLS connection
                # sometimes.
                self.connection.close()
            except:
                if self.fail_silently:
                    return
                raise
        finally:
            self.connection = None

    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        if not email_messages:
            return
        with self._lock:
            new_conn_created = self.open()
            if not self.connection:
                # We failed silently on open().
                # Trying to send would be pointless.
                return
            num_sent = 0
            for message in email_messages:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            if new_conn_created:
                self.close()
        return num_sent

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False
        if not email_message.to:
            return False
        from_email = sanitize_address(email_message.from_email, email_message.encoding)
        recipients = [sanitize_address(addr, email_message.encoding)
                      for addr in email_message.recipients()]
        message = email_message.message()
        charset = message.get_charset().get_output_charset() if message.get_charset() else 'utf-8'
        try:
            self.connection.sendmail(from_email, recipients,
                    force_bytes(message.as_string(), charset))
        except:
            if not self.fail_silently:
                raise
            return False
        email_dispatched.send(email_message, app=self.app)
        return True