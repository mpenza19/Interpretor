#!/bin/sh

.PHONY: clean

emor.ca: emor.a
	fst-compact $^ $@

emor.a: emor.fst
	fst-compiler $^ $@

emor.fst: lexicon
	perl/make-morph.perl $^ > $@

lexicon: xtag-morph-1.5a.txt
	perl/filter.perl $^| perl/morph-match.perl > $@

clean: 
	rm emor.ca emor.a emor.fst lexicon
