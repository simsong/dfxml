all:vmstats_pretty.dfxml vmstatsN

vmstats_pretty.dfxml: vmstats.py
	python3 vmstats.py --prettyprint vmstats_pretty.dfxml

vmstatsN: vmstats.py
	python3 vmstats.py --repeat  24 --interval 10 vmstatsN-new.dfxml
	/bin/mv -f vmstatsN-new.dfxml vmstatsN.dfxml

