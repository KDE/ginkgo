python setup.py sdist --formats=bztar
mv dist/*.tar.bz2 ~/Eclipse/Workspace-1/mdv-cooker-ginkgo/SOURCES/
cd po
for f in *.po; do msgmerge -vU $f ginkgo.pot; done
cd ..