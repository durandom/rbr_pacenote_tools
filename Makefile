.PHONY: all

all: janne-v3 bollinger-numeric smo-v3

janne-v3:
	./codriver.py --codriver janne-v3-numeric --list-ids > out/janne-v3-numeric-ids.csv
	@echo "Done"

bollinger-numeric:
	./codriver.py --codriver bollinger-numeric --list-ids > out/bollinger-numeric-ids.csv
	@echo "Done"

smo-v3:
	./codriver.py --codriver smo-v3 --list-ids > out/smo-v3-ids.csv
	@echo "Done"
