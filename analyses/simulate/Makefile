

all: results.txt check.log comparison.pdf slopes.txt

check.log:
	python check.py

slopes.dat: check.log
	grep Slope $< > $@

slopes.txt: slopes.dat
	./slopes.R > $@

results.txt:
	python make.py     # calls simulate.py
	python collect.py

comparison.pdf: results.txt
	./plot.R

