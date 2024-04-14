.PHONY: all

all: janne-v3 bollinger-numeric smo-v3

janne-v3:
	pipenv run ./codriver.py --codriver janne-v3-numeric --list-ids > out/janne-v3-numeric-ids.csv
	@echo "Done"

janne-v3-build:
	rm -rf build/janne-v3
	pipenv run ./codriver.py --codriver janne-v3-numeric --out build/janne-v3
	@echo "Done"

bollinger-numeric:
	pipenv run ./codriver.py --codriver bollinger-numeric --list-ids > out/bollinger-numeric-ids.csv
	@echo "Done"

bollinger-numeric-merge:
	pipenv run ./codriver.py --codriver janne-v3-numeric --merge out/bollinger-numeric-ids.csv --list-ids > out/merge-bollinger-numeric-ids.csv
	@echo "Done"

bollinger-numeric-merge-build:
	pipenv run ./codriver.py \
	  --codriver janne-v3-numeric \
	  --merge out/bollinger-numeric-ids.csv \
	  --merge-sound-dir assets/bollinger_sounds \
	  --out build/bollinger
	@echo "Done"

smo-v3:
	pipenv run ./codriver.py --codriver smo-v3 --list-ids > out/smo-v3-ids.csv
	@echo "Done"
