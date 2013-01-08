"""
Email backend that writes messages to console instead of sending them.
"""
import sys
import threading

from .base import BaseMail
from ..signals import email_dispatched

class Mail(BaseMail):
    def init_app(self, *args, **kwargs):
        self.stream = kwargs.pop('stream', sys.stdout)
        self._lock = threading.RLock()
        super(Mail, self).init_app(*args, **kwargs)

    def send_messages(self, email_messages):
        """Write all messages to the stream in a thread-safe way."""
        if not email_messages:
            return False
        with self._lock:
            try:
                stream_created = self.open()
                num_sent = 0
                for message in email_messages:
                    sent = self._send(message)
                    if sent:
                        num_sent += 1
                if stream_created:
                    self.close()
            except:
                if not self.fail_silently:
                    raise
        return num_sent

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not len(email_message.recipients()):
            return False
        if not len(email_message.to):
            return False
        if not email_message.from_email:
            return False
        
        self.stream.write('%s\n' % email_message.as_string())
        self.stream.write('-' * 79)
        self.stream.write('\n')
        self.stream.flush()  # flush after each message
        email_dispatched.send(email_message, app=self.app)
        return True