.PHONY: all

all: janne-v3 bollinger-numeric smo-v3

janne-v3:
	pipenv run ./codriver.py --codriver janne-v3-numeric --list-sounds > out/janne-v3-numeric-sounds.csv
	@echo "Done"

janne-v3-build:
	rm -rf build/janne-v3
	pipenv run ./codriver.py --codriver janne-v3-numeric --out build/janne-v3
	@echo "Done"

bollinger-numeric:
	pipenv run ./codriver.py --codriver bollinger-numeric --list-sounds > out/bollinger-numeric-sounds.csv
	@echo "Done"

bollinger-numeric-build:
	pipenv run ./codriver.py --codriver bollinger-numeric --out build/bollinger-numeric
	@echo "Done"

bollinger-numeric-merge:
	pipenv run ./codriver.py \
	  --codriver janne-v3-numeric \
	  --merge out/bollinger-numeric-sounds.csv \
	  --merge-sound-src-dir assets/bollinger_sounds \
	  --merge-language german \
	  --list-sounds > out/merge-bollinger-numeric-sounds.csv
	@echo "Done"

bollinger-numeric-merge-build:
	rm -rf build/bollinger-v3
	pipenv run ./codriver.py \
	  --codriver janne-v3-numeric \
	  --merge out/bollinger-numeric-sounds.csv \
	  --merge-sound-src-dir assets/bollinger_sounds \
	  --merge-sound-dir bollinger \
	  --merge-language german \
	  --out build/bollinger-v3
	@echo "Done"

smo-v3:
	pipenv run ./codriver.py --codriver smo-v3 --list-sounds > out/smo-v3-sounds.csv
	@echo "Done"
