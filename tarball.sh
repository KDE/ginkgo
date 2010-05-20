#!/bin/sh

VERSION="0.1.2"
SVN_BASE=http://svn.mandriva.com/svn/soft/nepomuk/ginkgo

rm -fr ginkgo-${VERSION}
rm -fr ginkgo-${VERSION}.tar.bz2
mkdir ginkgo-${VERSION}
cd ginkgo-${VERSION}

for entry in \
 src \
 po \
 ChangeLog \
 LICENSE \
 README \
 ginkgo \
; 



do svn export ${SVN_BASE}/$entry; done

cd ..

tar cvjf ginkgo-${VERSION}.tar.bz2 ginkgo-${VERSION}
mv ginkgo-${VERSION}.tar.bz2 ../mdv-cooker-ginkgo/SOURCES/

