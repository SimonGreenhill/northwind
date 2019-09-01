
all: results.pdf

plots:
	mkdir -p plots

results.dat: plots
	python make.py > results.dat
	mv *.pdf plots  # oops

results.pdf: results.dat
	Rscript -e "rmarkdown::render('results.Rmd')"

clean:
	rm -rf plots results.dat results.pdf
