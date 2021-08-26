#! /bin/sh
sphinx-apidoc -e -o . ../pandakota/
make html
touch _build/html/.nojekyll
