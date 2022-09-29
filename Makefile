#!/usr/bin/make -f

PACKAGE=logcontext

ifneq ($(wildcard /usr/share/sourcemgr/make/py),)
include /usr/share/sourcemgr/make/py
# availabe via http://github.com/smurfix/sourcemgr

else
%:
	@echo "Please use 'python3 -mbuild'."
	@exit 1
endif
