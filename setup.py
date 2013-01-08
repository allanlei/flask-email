"""
Flask-Email
----------

A Flask extension for sending email messages.

Port of Django's email backends and flask-mail.

Please refer to the online documentation for details.

Links
`````

* `documentation <http://packages.python.org/Flask-Email>`_
"""
from setuptools import setup


setup(
    name='Flask-Email',
    version='1.5',
    url='https://github.com/allanlei/flask-email',
    license='BSD',
    author='Allan Lei',
    author_email='allanlei@helveticode.com',
    description='Flask extension for sending email',
    long_description=__doc__,
    py_modules=[
        'flask_email'
    ],
    test_suite='nose.collector',
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask==0.9',,
        'six==1.2.0',
    ],
    tests_require=[
        'nose',
        'blinker',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)