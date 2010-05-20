#!/usr/bin/env python
# -*- coding: utf-8 -*-

## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE included in the packaging of
## this file. 
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
## See the NOTICE file distributed with this work for additional
## information regarding copyright ownership.

from distutils.core import setup
setup(name='ginkgo',
      version='0.1.4',
      url = 'http://wiki.mandriva.com/en/Ginkgo',
      download_url = 'http://svn.mandriva.com/svn/packages/cooker/ginkgo/current/SOURCES/',
      package_dir = {"": "src"},
      py_modules = ["ginkgo","resources_rc"],
      packages=["dao", "dialogs", "editors", "ontologies", "util", "views"],
      description='Ginkgo is a navigator for Nepomuk, the KDE semantic toolkit',
      data_files=[("/usr/bin/",["ginkgo"])],
      author='Stéphane Laurière',
      author_email='slauriere@mandriva.com',
      requires=['PyKDE4'],
      )
#                  ("/usr/share/locale/fr/LC_MESSAGES/ginkgo.mo", ["po/ginkgo.mo"]
#      install_requires=["PyKDE4",],
