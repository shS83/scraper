@echo off
del cache.html
git pull
py scraper.py
git add *
git commit -m Daily
git push
echo.
echo.
echo Everthing either woked like a charm of were fucked up beyond recognition.. ENJOY!
echo.
sleep 1
