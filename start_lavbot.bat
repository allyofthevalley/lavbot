@echo off
setlocal
cd /d "%~dp0"

rem Prevent inherited global Python env vars from breaking venv startup.
set "PYTHONHOME="
set "PYTHONPATH="

echo Starting Lavender TUI...
if exist ".venv-1\Scripts\python.exe" (
	".venv-1\Scripts\python.exe" lavender_tui.py
) else (
where python >nul 2>&1
if %errorlevel%==0 (
	python lavender_tui.py
	if %errorlevel% neq 0 (
		where py >nul 2>&1
		if %errorlevel%==0 py -3 lavender_tui.py
	)
) else (
	where py >nul 2>&1
	if %errorlevel%==0 py -3 lavender_tui.py
)
)

pause