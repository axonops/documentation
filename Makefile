#
#
#
.EXPORT_ALL_VARIABLES:
.ONESHELL:
.SHELL := /bin/bash
.PHONY: serve publish
# Default to use pipenv unless disabled
PIPENV=true
ifeq ($(PIPENV),true)
PIPENVCMD=pipenv run
else
PIPENVCMD=
endif

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

prep:
	[ "${PIPENV}" == "true" ] && pipenv install

serve: prep ## Serve locally the generated pages
	${PIPENVCMD} mkdocs serve

publish: prep ## Publish new docs
	${PIPENVCMD} mkdocs gh-deploy

