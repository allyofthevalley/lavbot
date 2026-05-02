@echo off
setlocal
title LavenderBot
cd /d "%~dp0"

rem Prevent inherited global Python env vars from breaking venv startup.
set "PYTHONHOME="
set "PYTHONPATH="

if exist ".venv-1\Scripts\python.exe" (
	".venv-1\Scripts\python.exe" bot.py
) else (
where python >nul 2>&1
if %errorlevel%==0 (
	python bot.py
	if %errorlevel% neq 0 (
		where py >nul 2>&1
		if %errorlevel%==0 py -3 bot.py
	)
) else (
	where py >nul 2>&1
	if %errorlevel%==0 py -3 bot.py
)
)

pause