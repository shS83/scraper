#!/bin/bash

echo "Scrape.sh version 0.0001 (c) shS 2024"

if [ -f cache.html ]; then
	echo "Old news found. Deleting..."
	rm cache.html
else
	echo "Good news, no old news. Getting latest."
fi

exec python scraper.py

echo \n
echo "Committing changes..."
echo \n

git add *
cit commit -m Daily
git push

if [ $1 ]; then
	if [ $1 == "--scheduled" ]; then
		read -t 5 -p "Paused for 5 seconds for convenience..."
	fi
fi

echo "All Done!"

