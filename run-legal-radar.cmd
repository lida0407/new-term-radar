@echo off
cd /d "%~dp0"
if "%~1"=="" (
  ".venv\Scripts\python.exe" -X utf8 -m radar daily --config config.legal-us.json --state state/legal-us --out report-legal-us.md
) else (
  ".venv\Scripts\python.exe" -X utf8 -m radar %* --config config.legal-us.json --state state/legal-us
)
exit /b %errorlevel%
