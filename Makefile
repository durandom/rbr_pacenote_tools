.PHONY: all

janne-v3:
	./codriver.py --codriver janne-v3-numeric --list-ids > out/janne-v3-numeric-ids.csv
	@echo "Done"

smo-v3:
	./codriver.py --codriver smo-v3 --list
	@echo "Done"
