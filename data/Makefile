ISOCODES = $(shell find jipa -depth 1 -iname '*.txt' | sed 's/.*/"&"/' | xargs -n1 awk '/ISO Code/ { getline; print $0 }' | sed s'/ //g' | sort -u)
JSONS := $(patsubst %,glottolog/%.json,$(ISOCODES))

.PHONY all: $(JSONS) glottolog/glottolog.dat glottolog/glottolog.trees

# glottolog classification details
glottolog/%.json:
	python ../bin/get_glottolog.py $* $@

glottolog/glottolog.dat: $(JSONS)
	python ../bin/get_glottolog_dat.py ./glottolog/ $@

glottolog/glottolog.trees: glottolog/glottolog.dat
	python ../bin/get_tree.py $< $@

# missing characters
missing:
	find jipa -name \*.txt -depth 1 -print0 | xargs -0 -n 1 ../bin/debug.py -q | grep 'MISSING' | tee 'debug.log'
	echo TOTAL CHARACTERS
	sed -E 's/^.*errors=//g' debug.log | sed -E 's|\).*||g' | sed -E 's|.*/||g' | paste -sd+ - | bc
	echo TOTAL MISSING
	sed -E 's/^.*errors=//g' debug.log | sed -E 's|/.*\).*||g' | paste -sd+ - | bc
	rm debug.log

# check
check:
	../bin/check.py jipa

# debugging helper to show target. Run make print-VARNAME
print-%  : ; @echo $* = $($*)
