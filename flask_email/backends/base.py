"""Base email backend class."""
from contextlib import contextmanager

from ..signals import email_dispatched

from ..message import (
    EmailMessage,
    SafeMIMEText, SafeMIMEMultipart,
    DEFAULT_ATTACHMENT_MIME_TYPE, make_msgid, forbid_multi_line_headers)

from ..exceptions import BadHeaderError


class BaseMail(object):
    """
    Base class for email backend implementations.

    Subclasses must at least overwrite send_messages().
    """
    def __init__(self, app=None):
        if app is not None: 
            self.init_app(app)

    def init_app(self, app, debug=False, fail_silently=None):
        """
        Initializes your mail settings from the application
        settings.

        You can use this if you want to set up your Mail instance
        at configuration time.

        :param app: Flask application instance
        :param fail_silently: Email fails silently on errors
        """
        if fail_silently is not None:
            self.fail_silently = fail_silently
        else:
            self.fail_silently = app.config.get('MAIL_FAIL_SILENTLY', False)
        self.debug = int(app.debug and debug)

        self.app = app
        
        # register extension with app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['email'] = self

    def open(self):
        """Open a network connection.

        This method can be overwritten by backend implementations to
        open a network connection.

        It's up to the backend implementation to track the status of
        a network connection if it's needed by the backend.

        This method can be called by applications to force a single
        network connection to be used when sending mails. See the
        send_messages() method of the SMTP backend for a reference
        implementation.

        The default implementation does nothing.
        """
        pass

    def close(self):
        """Close a network connection."""
        pass

    def __enter__(self):
        self.open()
        return self

    #Flask-mail
    def connect(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()

    def send(self, email_messages):
        return self.send_messages([email_messages])

    send_message = send

    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        raise NotImplementedError

    def send_mail(self, subject, body, from_email, to, **kwargs):
        """
        Easy wrapper for sending a single message to a recipient list. All members
        of the recipient list will see the other recipients in the 'To' field.

        If auth_user is None, the EMAIL_HOST_USER setting is used.
        If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

        Note: The API for this method is frozen. New code wanting to extend the
        functionality should use the EmailMessage class directly.
        """
        kwargs['connection'] = self
        fail_silently = kwargs.pop('fail_silently', False)
        return EmailMessage(subject=subject, body=body, from_email=from_email, to=to, **kwargs).send()

    def send_mass_mail(self, datatuple):
        """
        Given a datatuple of (subject, message, from_email, recipient_list), sends
        each message to each recipient list. Returns the number of emails sent.

        If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
        If auth_user and auth_password are set, they're used to log in.
        If auth_user is None, the EMAIL_HOST_USER setting is used.
        If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

        Note: The API for this method is frozen. New code wanting to extend the
        functionality should use the EmailMessage class directly.
        """
        connection = self
        messages = [EmailMessage(subject, message, sender, recipient,
                                 connection=connection)
                    for subject, message, sender, recipient in datatuple]
        return connection.send_messages(messages)


    def mail_admins(self, subject, message, fail_silently=False,
                    html_message=None):
        """Sends a message to the admins, as defined by the ADMINS setting."""
        # if not settings.ADMINS:
        #     return
        admins = app.config.get('ADMINS', None)
        if not admins:
            return
        connection = self
        mail = EmailMessage('%s%s' % (app.config.get('MAIL_EMAIL_SUBJECT_PREFIX', '[Flask] '), subject),
                    message, app.config.get('SERVER_EMAIL', 'root@localhost'), [a[1] for a in admins],
                    connection=connection)
        if html_message:
            mail.attach_alternative(html_message, 'text/html')
        mail.send(fail_silently=fail_silently)


    def mail_managers(self, subject, message, fail_silently=False,
                      html_message=None):
        """Sends a message to the managers, as defined by the MANAGERS setting."""
        # if not settings.MANAGERS:
            # return
        managers = app.config.get('MANAGERS', None)
        if not managers:
            return
        connection = self
        mail = EmailMessage('%s%s' % (app.config.get('MAIL_EMAIL_SUBJECT_PREFIX', '[Flask] '), subject),
                    message, app.config.get('SERVER_EMAIL', 'root@localhost'), [a[1] for a in managers],
                    connection=connection)
        if html_message:
            mail.attach_alternative(html_message, 'text/html')
        mail.send(fail_silently=fail_silently)

    @contextmanager
    def record_messages(self):
        """
        Records all messages. Use in unit tests for example::

            with mail.record_messages() as outbox:
                response = app.test_client.get("/email-sending-view/")
                assert len(outbox) == 1
                assert outbox[0].subject == "testing"

        You must have blinker installed in order to use this feature.
        :versionadded: 0.4
        """

        if not email_dispatched:
            raise RuntimeError("blinker must be installed")

        outbox = []

        def _record(message, app):
            outbox.append(message)

        email_dispatched.connect(_record)

        try:
            yield outbox
        finally:
            email_dispatched.disconnect(_record)