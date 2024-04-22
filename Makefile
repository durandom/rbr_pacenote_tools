.PHONY: all

all: janne-v3 bollinger-numeric smo-v3

janne-v2:
	pipenv run ./codriver.py --codriver janne-v2-numeric --list-sounds > out/janne-v2-numeric-sounds.csv
	@echo "Done"

janne-v2-unique:
	pipenv run ./codriver.py --codriver janne-v2-numeric --list-sounds --list-sounds-unique > out/janne-v2-numeric-sounds-unique.csv
	@echo "Done"

janne-v2-unique-id-name:
	pipenv run ./codriver.py --codriver janne-v2-numeric --list-sounds --list-sounds-unique --list-fields id,type,category,name > out/janne-v2-numeric-sounds-unique-id.csv
	@echo "Done"

janne-v3:
	pipenv run ./codriver.py --codriver janne-v3-numeric --list-sounds > out/janne-v3-numeric-sounds.csv
	@echo "Done"

janne-v3-unique:
	pipenv run ./codriver.py --codriver janne-v3-numeric --list-sounds --list-sounds-unique > out/janne-v3-numeric-sounds-unique.csv
	@echo "Done"

janne-v3-unique-id-name:
	pipenv run ./codriver.py --codriver janne-v3-numeric --list-sounds --list-sounds-unique --list-fields id,type,category,name > out/janne-v3-numeric-sounds-unique-id.csv
	@echo "Done"

janne-v3-build:
	rm -rf build/janne-v3
	pipenv run ./codriver.py --codriver janne-v3-numeric --out build/janne-v3
	@echo "Done"

bollinger-numeric:
	pipenv run ./codriver.py --codriver bollinger-numeric --list-sounds > out/bollinger-numeric-sounds.csv
	@echo "Done"

bollinger-numeric-unique:
	pipenv run ./codriver.py --codriver bollinger-numeric --list-sounds-unique --list-sounds > out/bollinger-numeric-sounds-unique.csv
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
	  --list-sounds-unique \
	  --list-sounds > out/merge-bollinger-numeric-sounds.csv
	@echo "Done"

# bollinger-numeric-merge-build:
# 	rm -rf build/bollinger-v3
# 	pipenv run ./codriver.py \
# 	  --codriver janne-v3-numeric \
# 	  --merge out/bollinger-numeric-sounds.csv \
# 	  --merge-sound-src-dir assets/bollinger_sounds \
# 	  --merge-sound-dir DavidBollinger \
# 	  --merge-language german \
# 	  --out build/bollinger-v3
# 	@echo "Done"

bollinger-v3: bollinger-numeric-unique
	grep -v "Not found" out/bollinger-numeric-sounds-unique.csv > out/bollinger-numeric-sounds-unique-no-error.csv
	pipenv run ./codriver.py \
	  --codriver janne-v3-numeric \
	  --merge out/bollinger-numeric-sounds-unique-no-error.csv \
	  --merge-sound-src-dir assets/bollinger_sounds \
	  --merge-language german \
	  --list-sounds-unique \
	  --list-sounds > out/merge-bollinger-numeric-sounds-unique.csv
	rm -rf build/bollinger-v3
	pipenv run ./codriver.py \
	  --codriver janne-v3-numeric \
	  --merge out/bollinger-numeric-sounds-unique-no-error.csv \
	  --merge-sound-src-dir assets/bollinger_sounds \
	  --merge-sound-dir DavidBollinger \
	  --merge-language german \
	  --out build/bollinger-v3
	@echo "Done"


smo-v3:
	pipenv run ./codriver.py --codriver smo-v3 --list-sounds > out/smo-v3-sounds.csv
	@echo "Done"

janne-v3-new-ids:
	pipenv run ./scripts/new_ids.py out/janne-v2-numeric-sounds-unique-id.csv out/janne-v3-numeric-sounds-unique-id.csv > out/janne-v3-new-ids.csv