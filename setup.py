"""
Flask-Email
----------

A Flask extension for sending email messages.

Port of Django's email backends.

Please refer to the online documentation for details.

Links
`````

* `documentation <http://packages.python.org/Flask-Email>`_
"""
from setuptools import setup
from setuptools import find_packages


setup(
    name='Flask-Email',
    version='1.4.3',
    url='https://github.com/allanlei/flask-email',
    license='BSD',
    author='Allan Lei',
    author_email='allanlei@helveticode.com',
    description='Flask extension for sending email',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
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