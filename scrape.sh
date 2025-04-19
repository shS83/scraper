#!/bin/bash
#
# INSTALLATION:
# 	export SCRAPER_DIR=/where/you/cloned_this...where scraper.py is
#

echo "Scrape.sh version 0.0002 (c) shS 2024"

if [[ -n $SCRAPER_DIR ]]; then
	cd $SCRAPER_DIR
fi

if [[ -f $(pwd)/scraper.py ]]; then
	echo "We are where we're supposed to be in... in $PWD"
else
	exit 1
fi

if [ -f .venv/Scripts/activate ]; then
	source .venv/Scripts/activate
elif [ -f .venv/bin/activate ]; then
	source .venv/bin/activate
else
	exit 1
fi

if [ -f cache.html ]; then
	echo "Old news found. Deleting..."
	rm cache.html
else
	echo "Good news, no old news. Getting latest."
fi

python scraper.py

echo
echo "Committing changes..."
echo

git add cache.html
git commit -m "Daily news push..."
git push

if [[ "$1" != "" ]]; then
	if [[ "$1" == "--scheduled" ]]; then
		echo "Pausing for 3 seconds or any key..."
		read -t 5 -p "_________"
	fi
fi

echo "All Done!"
deactivate
exit 0
