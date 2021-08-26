#! /bin/sh
sphinx-apidoc -e -o . ../pandakota/
make html
touch html/.nojekyll
