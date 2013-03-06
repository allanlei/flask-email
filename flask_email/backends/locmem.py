"""
Backend for test environment.
"""
import flask_email as mail
from .base import BaseMail


outbox = []

class Mail(BaseMail):
    """A email backend for use during test sessions.

    The test connection stores email messages in a dummy outbox,
    rather than sending them out on the wire.

    The dummy outbox is accessible through the outbox instance attribute.
    """
    def init_app(self, app, **kwargs):
        super(Mail, self).init_app(app, **kwargs)

    @property
    def outbox(self):
        return outbox

    def send_messages(self, messages):
        """Redirect messages to the dummy outbox"""
        global outbox
        outbox.extend(messages)
        return len(messages)
