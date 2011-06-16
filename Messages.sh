#!/bin/sh
# additional string for KAboutData
echo 'i18nc("NAME OF TRANSLATORS","Your names");' >> rc.py
echo 'i18nc("EMAIL OF TRANSLATORS","Your emails");' >> rc.py
$XGETTEXT -L python `find . -name \*.py` ginkgo -o $podir/ginkgo.pot
rm -f rc.py
