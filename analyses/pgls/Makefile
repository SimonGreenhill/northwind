#!/bin/make

all: correlations.pdf recovery.pdf

correlations.pdf: ../statistics/statistics.dat
	Rscript pgls.R

recovery.pdf: ../statistics/statistics.dat
	Rscript pgls-timetorecovery.R

clean:
	rm -rf *.dat *.pdf *.txt
