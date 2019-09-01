
all:

check:
	python check.py

make:
	python make.py

recovery_rate_bibles.pdf:
	./plot.R

missing.log:
	python missing.py > $@

clean:
	rm -rf *.log *.txt bibles/*

