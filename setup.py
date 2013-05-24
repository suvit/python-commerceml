# -*- coding: utf-8 -
#
# This file is part of python-commerceml released under the MIT license. 
# See the NOTICE for more information.

import os
import sys
from setuptools import setup, find_packages

from commerceml import VERSION


setup(
    name='django-tecdoc',
    version=VERSION,

    description='Itegration between python frameworks and 1c',
    long_description=file(
        os.path.join(
            os.path.dirname(__file__),
            'README.md'
        )
    ).read(),
    author='Victor Safronovich',
    author_email='vsafronovich@gmail.com',
    license='MIT',
    url='http://github.com/suvit/python-commerceml',
    zip_safe=False,
    packages=find_packages(exclude=['docs', 'examples', 'tests']),
    #install_requires='lxml',
    extras_require = {
        'django': ["django"],
    }
    include_package_data=True,
)
