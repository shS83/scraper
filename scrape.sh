#!/bin/bash

echo "Scrape.sh version 0.0002 (c) shS 2024"

if [ -f .venv/Scripts/activate ]; then
	source .venv/Scripts/activate
elif [ -f .venv/bin/activate ]; then
	source .venv/bin/activate
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

if [ "$1" != "" ]; then
	if [ "$1" == "--scheduled" ]; then
		echo "Pausing for 3 seconds or any key..."
		read -t 5 -p "_________"
	fi
fi

echo "All Done!"
deactivate
exit 0
