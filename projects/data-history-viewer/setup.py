# coding: utf-8

"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# To use a consistent encoding
from codecs import open
from os import path, getenv

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

NAME = "swagger_server"
VERSION = "1.0.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

here = path.abspath(path.dirname(__file__))

REQUIRES = ["connexion"]

setup(

    name='data-history-viewer',
    version=getenv("VERSION", "0.0.0-test"),
    description="Data History Query Service",
    long_description="""\
        Enable Trebuchet Data history queries using S3 LME Kafka data. Glue jobs convert recent
        data into a queryable Athena form. A general SQL query is presented to the micro-service
        API client. Pages of data can be retrieved for large data sets.
    """,

    author="jpowell",
    author_email="jpowell@datapipe.com",
    url="https://scm.trebuchetdev.com/analytics/data-history-viewer",
    keywords=["swagger", "data history query service", "aws", "history", "athena"],

    install_requires=[l.strip() for l in open(path.join(here, "requirements.txt"), "r")],

    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
                  # How mature is this project? Common values are
                  #   3 - Alpha
                  #   4 - Beta
                  #   5 - Production/Stable
                  'Development Status :: 3 - Alpha',

                  # Indicate who your project is intended for
                  'Intended Audience :: Datapipe internal Developers',
                  'Topic :: Software Development :: Data Analysis',

                  # Specify the Python versions you support here. In particular, ensure
                  # that you indicate whether you support Python 2, Python 3 or both.
                  'Programming Language :: Python :: 2',
                  'Programming Language :: Python :: 2.7',
                  'Programming Language :: Python :: 3',
                  'Programming Language :: Python :: 3.3',
                  'Programming Language :: Python :: 3.4',
                  'Programming Language :: Python :: 3.5',
                  'Programming Language :: Python :: 3.6',
              ]

)


