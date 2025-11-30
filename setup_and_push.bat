@echo off
cd D:\HAK\MasterOsint

echo Initializing git repository...
git init

echo Adding all files...
git add -A

echo Creating initial commit...
git commit -m "Initial commit: PHINEAS OSINT Framework - Comprehensive OSINT automation with free tools, no emojis, clean and professional"

echo Setting main branch...
git branch -M main

echo Adding remote...
git remote add origin https://github.com/kamakauzy/PHINEAS.git

echo Pushing to GitHub...
git push -u origin main --force

echo.
echo Done! Check https://github.com/kamakauzy/PHINEAS
pause
