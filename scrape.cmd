@echo off
del cache.html
git pull
py scraper.py
git add *
git commit -m Daily
git push
pause
