.. Flask-Email documentation master file, created by
   sphinx-quickstart on Wed Mar  6 14:39:00 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. module:: flask-email

.. include:: ../README.rst

TODO: Finish documentation

.. include:: ../INSTALL.rst


Usage
-----

Instantiate a email backend::

    from flask import Flask
    from flask.ext.email import ConsoleMail

    app = Flask(__name__)
    mailbox = ConsoleMail(app)

or initialize it later :meth:`~.Mail.init_app`::

    mailbox = ConsoleMail()

    def create_app(config='settings.cfg'):
        app = Flask(__name__)
        app.config.from_pyfile(config)
        mailbox.init_app(app)
        return app


Sending an Email
~~~~~~~~~~~~~~~~

.. code-block:: python

    email = EmailMessage(
        'Subject', 
        'Content', 
        'bounce@example.com', 
        ['to@example.com'], 
        headers={'From': 'from@example.com'}
    )
    email.send(mailbox)

Shortcuts
~~~~~~~~~

.. code-block:: python

    send_mail('Subject', 'Content', 'bounce@example.com', ['to@example.com'])

Configuration
-------------

Flask-Email accepts the following settings regardless of email backend

``DEFAULT_CHARSET``
    Default charset to use for all :class:`EmailMessage`.

    Defaults to ``'utf-8'``

``DEFAULT_FROM_EMAIL``
    Default email address to use for when the `sender` parameter not 
    present.

    Defaults to ``'webmaster@localhost'``

``SERVER_EMAIL``
    The email address that messages come from when using :meth:`mail_admins` and
    :meth:`mail_managers` and no `sender` is provided.

    Defaults to ``'root@localhost'``

``EMAIL_SUBJECT_PREFIX``
    Subject-line prefix for email messages sent with :meth:`mail_admins` or 
    :meth:`mail_managers`. You’ll probably want to include the trailing space.

    Defaults to ``'[Flask] '``

``ADMINS``
    A tuple following one of the below formats that specifies who should receive
    messages from :meth:`mail_admins`.

    Tuple of ``name`` and ``email``::
    
    	(('John', 'john@example.com'), ('Mary', 'mary@example.com'))

    Email format ``name <email>``::

    	('John <john@example.com>', 'Mary <mary@example.com>')

    Defaults to ``() (Empty tuple)``

``MANAGERS``
    A tuple in the same format as ADMINS that specifies who should receive 
    messages from :meth:`mail_managers`

    Defaults to ``() (Empty tuple)``

``EMAIL_BACKEND``
    The backend to use for sending emails.

    Defaults to ``'flask.ext.email.backends.locmem.Mail'``


Email Backends
--------------

SMTPMail
~~~~~~~~

.. automodule:: flask.ext.email.backends.smtp


``EMAIL_HOST``
    The host to use for sending email.

    Defaults to ``'localhost'``

``EMAIL_PORT``
    Port to use for the SMTP server defined in `EMAIL_HOST`.

    Defaults to ``25``

``EMAIL_HOST_USER``
    Username to use for the SMTP server defined in `EMAIL_HOST`. If empty, 
    authentication will be skipped.

    Defaults to ``'' (Empty string)``

``EMAIL_HOST_PASSWORD``
    Password to use for the SMTP server defined in `EMAIL_HOST`. This setting is 
    used in conjunction with `EMAIL_HOST_USER` when authenticating to the SMTP 
    server. If either of these settings is empty, authentication will be skipped.

    Defaults to ``'' (Empty string)``

``EMAIL_USE_TLS``
    Whether to use a TLS (secure) connection when talking to the SMTP server.

    Defaults to ``False``

``EMAIL_USE_SSL``
    Whether to use a TLS (secure) connection when talking to the SMTP server.

    Defaults to ``False``

.. autoclass:: flask.ext.email.backends.smtp.Mail
   :members:

   alias :class:`flask.ext.email.SMTPMail`

FilebasedMail
~~~~~~~~~~~~~

.. automodule:: flask.ext.email.backends.filebased

``EMAIL_FILE_PATH``
    The directory used by the file email backend to store output files.

    Defaults to ``None``

.. autoclass:: flask.ext.email.backends.filebased.Mail
    :members:

    alias :class:`flask.ext.email.FilebasedMail`


ConsoleMail
~~~~~~~~~~~
.. automodule:: flask.ext.email.backends.console

.. autoclass:: flask.ext.email.backends.console.Mail
   :members: init_app


DummyMail
~~~~~~~~~
.. automodule:: flask.ext.email.backends.dummy

.. autoclass:: flask.ext.email.backends.dummy.Mail
   :members:

   alias :class:`flask.ext.email.DummyMail`


LocmemMail
~~~~~~~~~~

.. autoclass:: flask.ext.email.backends.locmem.Mail
   :members:

   alias :class:`flask.ext.email.LocmemMail`


API
---


.. automethod:: flask.ext.email.send_mail

.. automethod:: flask.ext.email.mail_admins

.. automethod:: flask.ext.email.mail_managers

.. autoclass:: flask.ext.email.message.EmailMessage
    :members:

.. autoclass:: flask.ext.email.message.EmailMultiAlternatives
    :members:

Extend
------

.. autoclass:: flask.ext.email.backends.base.BaseMail
   :members:

.. include:: ../CHANGES.rst

Notes
-----



.. _Flask: http://flask.pocoo.org
.. _Django: https://www.djangoproject.com/