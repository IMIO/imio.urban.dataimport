#!/usr/bin/make
#
#
#options =

.PHONY: test instance cleanall portals

all: test

bin/python:
		virtualenv-2.6 --no-site-packages .

develop-eggs: bin/python bootstrap.py
		./bin/python bootstrap.py

bin/buildout: develop-eggs

bin/test: versions.cfg buildout.cfg bin/buildout setup.py
		./bin/buildout -Nvt 5
			touch $@

bin/instance: versions.cfg buildout.cfg bin/buildout setup.py
		./bin/buildout -Nvt 5 install instance
			touch $@

test: bin/test
		bin/test -s Products.urban $(options)

instance: bin/instance
		bin/instance fg

cleanall:
		rm -fr bin develop-eggs downloads eggs parts 
