#!/bin/make

all: signal.pdf pgls.pdf correlations.pdf

signal.pdf: ../statistics/statistics.dat
	Rscript -e "rmarkdown::render('signal.Rmd')"

pgls.pdf: ../statistics/statistics.dat
	Rscript -e "rmarkdown::render('pgls.Rmd')"

correlations.pdf: ../statistics/statistics.dat
	Rscript pgls-better.R

clean:
	rm *.dat *.pdf
