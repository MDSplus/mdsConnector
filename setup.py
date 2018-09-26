#!/usr/bin/env python
import sys
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.version_info < (2, 5):
    sys.exit("requires python 2.5 and up")

here = os.path.dirname(__file__)
version_string='1.5'

setup(name = "mdsconnector",
    version = version_string, 
    description = "Remote call to MDSplus objects",
    author = "MDSplus Core Development Team",
    author_email = "mdsplus_dev@psfc.mit.edu",
    maintainer_email = "mdsplus_dev@psfc.mit.edu",
    license = "MIT",
    url = "http://www.mdsplus.org",
    py_modules = [
        'mdsconnector',
    ],
    scripts = [
    ],
    install_requires = ["rpyc","dill"],
    platforms = ["POSIX", "Windows"],
    use_2to3 = False,
    zip_safe = False,
    long_description = """
The mdsConnector class enables the connection to a remote system via
SSH to utilize the MDSplus python objects remotely on that system.""",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Object Brokering",
        "Topic :: System :: Clustering",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
