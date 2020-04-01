
all: coverage.dat recovery_rate.log predict-gamm.dat is-gamm-better-than-lm.txt predicted_length_vs_inventory.txt

coverage.dat:
	python get.py

recovery_rate.log: coverage.dat
	Rscript recovery_rate.r > $@

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
