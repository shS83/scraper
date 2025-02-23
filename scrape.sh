#!/bin/bash

echo "Scrape.sh version 0.0001 (c) shS 2024"

.venv/Scripts/activate&

if [ -f cache.html ]; then
	echo "Old news found. Deleting..."
	rm cache.html
else
	echo "Good news, no old news. Getting latest."
fi

python scraper.py&

echo
echo "Committing changes..."
echo

git add cache.html
git commit -m Daily
git push

if [ $1 ]; then
	if [ $1 == "--scheduled" ]; then
		echo "Pausing for 3 seconds or any key..."
		read -t 5 -p "_________"
	fi
fi

echo "All Done!"
deactivate&
