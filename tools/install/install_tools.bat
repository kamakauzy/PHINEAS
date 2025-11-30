@echo off
REM PHINEAS Tool Installation Script for Windows
REM Installs free OSINT tools for PHINEAS framework

echo.
echo PHINEAS Tool Installation
echo ================================
echo.

echo Installing Python OSINT tools...
echo.

pip install sherlock-project && echo [OK] Sherlock installed || echo [FAIL] Sherlock failed
pip install holehe && echo [OK] Holehe installed || echo [FAIL] Holehe failed
pip install theHarvester && echo [OK] theHarvester installed || echo [FAIL] theHarvester failed
pip install sublist3r && echo [OK] Sublist3r installed || echo [OK] Sublist3r failed
pip install maigret && echo [OK] Maigret installed || echo [FAIL] Maigret failed
pip install phoneinfoga && echo [OK] PhoneInfoga installed || echo [FAIL] PhoneInfoga failed
pip install h8mail && echo [OK] h8mail installed || echo [FAIL] h8mail failed

echo.
echo Installation complete!
echo.
echo Next steps:
echo   1. Configure API keys: python phineas.py setup
echo   2. Run a scan: python phineas.py scan --target example@email.com
echo   3. View plugins: python phineas.py plugins
echo.
echo Tips:
echo   - Most tools work without API keys
echo   - Get free API keys for enhanced features
echo   - See README.md for full documentation
echo.
pause
