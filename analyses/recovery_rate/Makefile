
all: coverage.dat plot.log predict-lm.dat predict-gamm.dat is-gamm-better-than-lm.txt predicted_length_vs_inventory.txt

coverage.dat:
	python get.py

plot.log: coverage.dat
	Rscript plot.r > $@

predict-lm.dat: coverage.dat
	Rscript predict-lm.r

predict-gamm.dat: coverage.dat
	Rscript predict-gamm.r

is-gamm-better-than-lm.txt: predict-gamm.dat
	Rscript is-gamm-better-than-lm.r > $@

predicted_length_vs_inventory.txt: predict-gamm.dat
	Rscript predicted_length_vs_inventory.R

clean:
	rm -rf *.dat
	rm -rf *.pdf
	rm -rf *.png
	rm -rf *.log
