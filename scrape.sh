#!/bin/bash

echo "Scrape.sh version 0.0001 (c) shS 2024"

exec source .venv/Scripts/activate&

if [ -f cache.html ]; then
	echo "Old news found. Deleting..."
	rm cache.html
else
	echo "Good news, no old news. Getting latest."
fi

exec python scraper.py&

echo \n
echo "Committing changes..."
echo \n

git add *
git commit -m Daily
git push

if [ $1 ]; then
	if [ $1 == "--scheduled" ]; then
		echo "Pausing for 3 seconds or any key..."
		read -t 5
	fi
fi

echo "All Done!"
exec "deactivate"
