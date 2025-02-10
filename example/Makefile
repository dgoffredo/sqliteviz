.PHONY: all
all: schema.svg gnupg.svg multikey.svg

%.svg: %.sql ../__main__.py
	python ../ $< | dot -Tsvg >$@

