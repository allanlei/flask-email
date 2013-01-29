"""
Dummy email backend that does nothing.
"""
from .base import BaseMail

class Mail(BaseMail):
    def send_messages(self, email_messages):
        return len(email_messages)
