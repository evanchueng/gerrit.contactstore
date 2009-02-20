# gerrit-contactstore for Google App Engine
#
# Define APPID to the unique Google App Engine application instance
# 'make update' will upload the application files to.
#
# Define APPSEC to the security token clients must present in order
# to upload to this application instance.  Default is to generate
# a random string.
#
# Define APPCFG to the location of appcfg.py from the Google App
# Engine SDK download.
#

APPID   = gerrit-contactstore
APPSEC  = $(shell sh -c 'dd if=/dev/urandom bs=128 count=1 2>/dev/null | md5sum | sed s/-//')
APPCFG  = appcfg.py
CPIO    = cpio -pd

ifeq ($(shell uname),Darwin)
	APPCFG = python /usr/local/bin/appcfg.py
endif

-include config.mak

R_WEB      := release/web

WEB_INCLUDE := $(strip \
	app.yaml \
	index.yaml \
	static \
	*.py \
)

release-web:
	@echo Building gerrit-contactstore `../GIT-VERSION-GEN`  for $(APPID):
	@rm -rf $(R_WEB)
	@mkdir -p $(R_WEB)
	@echo "  Copying loose files" && \
	 find $(WEB_INCLUDE) -print | $(CPIO) $(abspath $(R_WEB))
	@../GIT-VERSION-GEN >$(R_WEB)/static/application_version
	@perl -pi -e 's/(application:).*/$$1 $(APPID)/' $(R_WEB)/app.yaml
	@a=$(APPSEC);echo "APPSEC='$$a'" >$(R_WEB)/appsec.py
	@cat $(R_WEB)/appsec.py
	@echo $(R_WEB) built for $(APPID).

update: release-web
	$(APPCFG) $(APPCFG_OPTS) update $(R_WEB)

version:
	@printf '%s = ' '$(APPID)'
	@curl http://$(APPID).appspot.com/application_version

clean:
	@rm -rf release *.pyc
