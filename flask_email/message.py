from __future__ import unicode_literals

from email import charset as Charset, encoders as Encoders
from email.generator import Generator
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formatdate, getaddresses, formataddr, parseaddr

from .exceptions import BadHeaderError
from .encoding import force_text
from .utils import DNS_NAME

import six
import mimetypes
import os
import random
import sys
import time

from flask import current_app as app

from email.utils import make_msgid
# Copied from Python standard library, with the following modifications:
# * Used cached hostname for performance.
# * Added try/except to support lack of getpid() in Jython (#5496).
def make_msgid(idstring=None):
    """Returns a string suitable for RFC 2822 compliant Message-ID, e.g:

    <20020201195627.33539.96671@nightshade.la.mastaler.com>

    Optional idstring if given is a string used to strengthen the
    uniqueness of the message id.
    """
    timeval = time.time()
    utcdate = time.strftime('%Y%m%d%H%M%S', time.gmtime(timeval))
    try:
        pid = os.getpid()
    except AttributeError:
        # No getpid() in Jython, for example.
        pid = 1
    randint = random.randrange(100000)
    if idstring is None:
        idstring = ''
    else:
        idstring = '.' + idstring
    idhost = DNS_NAME
    msgid = '<%s.%s.%s%s@%s>' % (utcdate, pid, randint, idstring, idhost)
    return msgid

# Don't BASE64-encode UTF-8 messages so that we avoid unwanted attention from
# some spam filters.
Charset.add_charset('utf-8', Charset.SHORTEST, None, 'utf-8')

# Default MIME type to use on attachments (if it is not explicitly given
# and cannot be guessed).
DEFAULT_ATTACHMENT_MIME_TYPE = 'application/octet-stream'

# Header names that contain structured address data (RFC #5322)
ADDRESS_HEADERS = set([
    'from',
    'sender',
    'reply-to',
    'to',
    'cc',
    'bcc',
    'resent-from',
    'resent-sender',
    'resent-to',
    'resent-cc',
    'resent-bcc',
])



def sanitize_address(addr, encoding):
    if isinstance(addr, six.string_types):
        addr = parseaddr(force_text(addr))
    nm, addr = addr
    # This try-except clause is needed on Python 3 < 3.2.4
    # http://bugs.python.org/issue14291
    try:
        nm = Header(nm, encoding).encode()
    except UnicodeEncodeError:
        nm = Header(nm, 'utf-8').encode()
    try:
        addr.encode('ascii')
    except UnicodeEncodeError:  # IDN
        if '@' in addr:
            localpart, domain = addr.split('@', 1)
            localpart = str(Header(localpart, encoding))
            domain = domain.encode('idna').decode('ascii')
            addr = '@'.join([localpart, domain])
        else:
            addr = Header(addr, encoding).encode()
    return formataddr((nm, addr))


def forbid_multi_line_headers(name, val, encoding):
    """Forbids multi-line headers, to prevent header injection."""
    encoding = encoding or app.config.get('DEFAULT_CHARSET', 'utf-8')
    val = force_text(val)
    if '\n' in val or '\r' in val:
        raise BadHeaderError("Header values can't contain newlines (got %r for header %r)" % (val, name))
    try:
        val.encode('ascii')
    except UnicodeEncodeError:
        if name.lower() in ADDRESS_HEADERS:
            val = ', '.join(sanitize_address(addr, encoding)
                for addr in getaddresses((val,)))
        else:
            val = Header(val, encoding).encode()
    else:
        if name.lower() == 'subject':
            val = Header(val).encode()
    return str(name), val


class SafeMIMEText(MIMEText):
    def __init__(self, text, subtype, charset):
        self.encoding = charset
        MIMEText.__init__(self, text, subtype, charset)

    def __setitem__(self, name, val):
        name, val = forbid_multi_line_headers(name, val, self.encoding)
        MIMEText.__setitem__(self, name, val)

    def as_string(self, unixfrom=False):
        """Return the entire formatted message as a string.
        Optional `unixfrom' when True, means include the Unix From_ envelope
        header.

        This overrides the default as_string() implementation to not mangle
        lines that begin with 'From '. See bug #13433 for details.
        """
        fp = six.StringIO()
        g = Generator(fp, mangle_from_ = False)
        if sys.version_info < (2, 6, 6) and isinstance(self._payload, six.text_type):
            # Workaround for http://bugs.python.org/issue1368247
            self._payload = self._payload.encode(self._charset.output_charset)
        g.flatten(self, unixfrom=unixfrom)
        return fp.getvalue()


class SafeMIMEMultipart(MIMEMultipart):
    def __init__(self, _subtype='mixed', boundary=None, _subparts=None, encoding=None, **_params):
        self.encoding = encoding
        MIMEMultipart.__init__(self, _subtype, boundary, _subparts, **_params)

    def __setitem__(self, name, val):
        name, val = forbid_multi_line_headers(name, val, self.encoding)
        MIMEMultipart.__setitem__(self, name, val)

    def as_string(self, unixfrom=False):
        """Return the entire formatted message as a string.
        Optional `unixfrom' when True, means include the Unix From_ envelope
        header.

        This overrides the default as_string() implementation to not mangle
        lines that begin with 'From '. See bug #13433 for details.
        """
        fp = six.StringIO()
        g = Generator(fp, mangle_from_ = False)
        g.flatten(self, unixfrom=unixfrom)
        return fp.getvalue()


class FlaskEmailMessageCompat(object):
    def __init__(self, *args, **kwargs):
        kwargs['encoding'] = kwargs.pop('charset', None)
        html = kwargs.pop('html', None)
        kwargs['headers'] = kwargs.pop('extra_headers', None)
        self.date = kwargs.pop('date', None)
        super(FlaskEmailMessageCompat, self).__init__(*args, **kwargs)
        
        if isinstance(self.from_email, tuple):
            # sender can be tuple of (name, address)
            self.from_email = "%s <%s>" % self.from_email
        self.html = html

    @property
    def html(self):
        return self._html

    @html.setter
    def html(self, value):
        self._html = value
        if self._html:
            #Attach as alternative
            self.attach_alternative(content=self._html, mimetype='text/html')

    @property
    def send_to(self):
        return set(self.to) | set(self.bcc or ()) | set(self.cc or ())

    def recipients(self):
        return list(self.send_to)

    def add_recipient(self, recipient):
        self.to.append(recipient)

    def as_string(self):
        return self.message().as_string()

    def attach(self, *args, **kwargs):
        kwargs.setdefault('mimetype', kwargs.pop('content_type', None))
        return super(FlaskEmailMessageCompat, self).attach(*args, **kwargs)

    def __unicode__(self):
        return str(self)

    def __str__(self):
        return self.as_string()


class BaseEmailMessage(object):
    """
    A container for email information.
    """
    content_subtype = 'plain'
    mixed_subtype = 'mixed'
    alternative_subtype = 'alternative'
    encoding = None     # None => use settings default

    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
                 connection=None, attachments=None, alternatives=None, headers=None, cc=None, reply_to=None, encoding=None):
        """
        Initialize a single email message (which can be sent to multiple
        recipients).

        All strings used to create the message can be unicode strings
        (or UTF-8 bytestrings). The SafeMIMEText class will handle any
        necessary encoding conversions.
        """
        if to:
            assert not isinstance(to, six.string_types), '"to" argument must be a list or tuple'
            self.to = list(to)
        else:
            self.to = []
        if cc:
            assert not isinstance(cc, six.string_types), '"cc" argument must be a list or tuple'
            self.cc = list(cc)
        else:
            self.cc = []
        if bcc:
            assert not isinstance(bcc, six.string_types), '"bcc" argument must be a list or tuple'
            self.bcc = list(bcc)
        else:
            self.bcc = []
        self.from_email = from_email or app.config.get('DEFAULT_FROM_EMAIL')
        self.reply_to = reply_to
        self.subject = subject
        self.body = body
        self.attachments = attachments or []
        self.alternatives = alternatives or []
        self.extra_headers = headers or {}
        self.connection = connection    # Instance of Mail()
        self.encoding = encoding or app.config.get('DEFAULT_CHARSET', 'utf-8')
        self.msgId = make_msgid()

    def message(self):
        msg = SafeMIMEText(self.body, self.content_subtype, self.encoding)
        msg = self._create_message(msg)
        msg['Subject'] = self.subject
        msg['From'] = self.extra_headers.get('From', self.from_email)
        msg['To'] = self.extra_headers.get('To', ', '.join(self.to))
        if self.cc:
            msg['Cc'] = ', '.join(self.cc)
        if self.bcc:
            msg['Bcc'] = ', '.join(self.bcc)
        if self.reply_to:
            msg['Reply-To'] = self.reply_to

        # Email header names are case-insensitive (RFC 2045), so we have to
        # accommodate that when doing comparisons.
        header_names = [key.lower() for key in self.extra_headers]
        if 'date' not in header_names:
            msg['Date'] = formatdate(self.date)
        if 'message-id' not in header_names:
            msg['Message-ID'] = self.msgId
        for name, value in self.extra_headers.items():
            if name.lower() in ('from', 'to'):  # From and To are already handled
                continue
            msg[name] = value
        return msg

    def recipients(self):
        """
        Returns a list of all recipients of the email (includes direct
        addressees as well as Cc and Bcc entries).
        """
        return self.to + self.cc + self.bcc

    def send(self, fail_silently=False):
        """Sends the email message."""
        if not self.recipients():
            # Don't bother creating the network connection if there's nobody to
            # send to.
            return 0
        return self.connection.send_messages([self])

    def attach(self, filename=None, content=None, mimetype=None):
        """
        Attaches a file with the given filename and content. The filename can
        be omitted and the mimetype is guessed, if not provided.

        If the first parameter is a MIMEBase subclass it is inserted directly
        into the resulting message attachments.
        """
        if isinstance(filename, MIMEBase):
            assert content == mimetype == None
            self.attachments.append(filename)
        else:
            assert content is not None
            self.attachments.append((filename, content, mimetype))

    def attach_file(self, path, mimetype=None):
        """Attaches a file from the filesystem."""
        filename = os.path.basename(path)
        with open(path, 'rb') as f:
            content = f.read()
        self.attach(filename, content, mimetype)

    def attach_alternative(self, content, mimetype):
        """Attach an alternative content representation."""
        assert content is not None
        assert mimetype is not None
        self.alternatives.append((content, mimetype))

    def _create_message(self, msg):
        return self._create_attachments(self._create_alternatives(msg))

    def _create_attachments(self, msg):
        if self.attachments:
            body_msg = msg
            msg = SafeMIMEMultipart(_subtype=self.mixed_subtype, encoding=self.encoding)
            if self.body:
                msg.attach(body_msg)
            for attachment in self.attachments:
                if isinstance(attachment, MIMEBase):
                    msg.attach(attachment)
                else:
                    msg.attach(self._create_attachment(*attachment))
        return msg

    def _create_alternatives(self, msg):
        if self.alternatives:
            body_msg = msg
            msg = SafeMIMEMultipart(_subtype=self.alternative_subtype, encoding=self.encoding)
            if self.body:
                msg.attach(body_msg)
            for alternative in self.alternatives:
                msg.attach(self._create_mime_attachment(*alternative))
        return msg

    def _create_mime_attachment(self, content, mimetype):
        """
        Converts the content, mimetype pair into a MIME attachment object.
        """
        basetype, subtype = mimetype.split('/', 1)
        if basetype == 'text':
            encoding = self.encoding or app.config.get('DEFAULT_CHARSET', 'utf-8')
            attachment = SafeMIMEText(content, subtype, encoding)
        else:
            # Encode non-text attachments with base64.
            attachment = MIMEBase(basetype, subtype)
            attachment.set_payload(content)
            Encoders.encode_base64(attachment)
        return attachment

    def _create_attachment(self, filename, content, mimetype=None):
        """
        Converts the filename, content, mimetype triple into a MIME attachment
        object.
        """
        if mimetype is None:
            mimetype, _ = mimetypes.guess_type(filename)
            if mimetype is None:
                mimetype = DEFAULT_ATTACHMENT_MIME_TYPE
        attachment = self._create_mime_attachment(content, mimetype)
        if filename:
            try:
                filename.encode('ascii')
            except UnicodeEncodeError:
                if not six.PY3:
                    filename = filename.encode('utf-8')
                filename = ('utf-8', '', filename)
            attachment.add_header('Content-Disposition', 'attachment',
                                  filename=filename)
        return attachment
    
class EmailMessage(FlaskEmailMessageCompat, BaseEmailMessage):
    pass