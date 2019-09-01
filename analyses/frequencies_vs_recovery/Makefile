
all: results.log

results.dat:
	python get_rates.py $@

results.log: results.dat
	Rscript plot.r > $@

clean:
	rm results.dat results.log *.pdf
