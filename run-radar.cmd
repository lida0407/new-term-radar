@echo off
cd /d "%~dp0"
if "%~1"=="" (
  ".venv\Scripts\python.exe" -X utf8 -m radar daily --skip x,sitemaps,newsites,gsc,review,judge,usecases --out report.md
) else (
  ".venv\Scripts\python.exe" -X utf8 -m radar %*
)
exit /b %errorlevel%
