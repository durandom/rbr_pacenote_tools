.PHONY: all

all: janne-v3 bollinger-numeric smo-v3

janne-v3:
	./codriver.py --codriver janne-v3-numeric --list-ids > out/janne-v3-numeric-ids.csv
	@echo "Done"

bollinger-numeric:
	./codriver.py --codriver bollinger-numeric --list-ids > out/bollinger-numeric-ids.csv
	@echo "Done"

merge-bollinger-numeric:
	./codriver.py --codriver janne-v3-numeric --merge out/bollinger-numeric-ids.csv --list-ids > out/merge-bollinger-numeric-ids.csv
	@echo "Done"

build-bollinger-numeric:
	./codriver.py --codriver janne-v3-numeric --merge out/bollinger-numeric-ids.csv --out build/bollinger
	@echo "Done"

smo-v3:
	./codriver.py --codriver smo-v3 --list-ids > out/smo-v3-ids.csv
	@echo "Done"
