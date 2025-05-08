#!/bin/bash
#
# INSTALLATION:
# 	export SCRAPER_DIR=/where/you/cloned_this...where scraper.py is
#

echo "Scrape.sh version 0.0002 (c) shS 2024"

CDIR=$(pwd)
SCRAPER_DIR=$SCRAPER_DIR

if [[ $SCRAPER_DIR == "" ]]; then
	printf 'Please set the ENVIRONMENT variable SCRAPER_DIR'
	exit 1
fi

if [[ -f $SCRAPER_DIR/scraper.py ]]; then
	echo "We are where we're supposed to be in... in $PWD"
else
	exit 1
fi

if [[ -f $SCRAPER_DIR/.venv/Scripts/activate ]]; then
	source $SCRAPER_DIR/.venv/Scripts/activate
elif [[ -f $SCRAPER_DIR/.venv/bin/activate ]]; then
	source $SCRAPER_DIR/.venv/bin/activate
else
	exit 1
fi

if [[ -f $SCRAPER_DIR/cache.html ]]; then
	echo "Old news found. Deleting..."
	rm cache.html -f
else
	echo "Good news, no old news. Getting latest."
fi

cd $SCRAPER_DIR/

python ./scraper.py

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
