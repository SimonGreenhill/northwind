#!/bin/make

all: statistics.pdf charitable.pdf errors.pdf errors.txt summary_histograms.pdf correlations.pdf overall.txt

statistics.dat:
	python get_statistics.py > $@

statistics.pdf: statistics.dat
	Rscript -e "rmarkdown::render('statistics.Rmd')" > $@.log
	rm -rf figure $@.log

charitable.pdf: statistics.dat
	Rscript -e "rmarkdown::render('charitable.Rmd')" > $@.log
	rm -rf figure $@.log

correlations.pdf: statistics.dat
	Rscript -e "rmarkdown::render('correlations.Rmd')" > $@.log
	rm -rf figure $@.log

errors.pdf: statistics.dat
	Rscript -e "rmarkdown::render('errors.Rmd')" > $@.log
	rm -rf figure $@.log

summary_histograms.pdf: statistics.dat
	Rscript summary_histograms.r

overall.txt:
	python overall.py > $@

errors.txt:
	python errors.py > $@

clean:
	rm *.dat *.pdf *.txt
