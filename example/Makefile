.PHONY: all
all: schema.svg gnupg.svg multikey.svg sakila.svg

%.svg: %.sql ../__main__.py
	python ../ $< | dot -Tsvg >$@

