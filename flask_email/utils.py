"""
Tools for sending email.
"""
from __future__ import unicode_literals

import socket

# Cache the hostname, but do it lazily: socket.getfqdn() can take a couple of
# seconds, which slows down the restart of the server.
class CachedDnsName(object):
    def __str__(self):
        return self.get_fqdn()

    def get_fqdn(self):
        if not hasattr(self, '_fqdn'):
            self._fqdn = socket.getfqdn()
        return self._fqdn

DNS_NAME = CachedDnsName()