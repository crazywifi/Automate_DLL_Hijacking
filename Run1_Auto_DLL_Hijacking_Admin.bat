@echo off
REM Change to the directory of the batch file
cd /d %~dp0

REM Execute the first Python script
python DLLHijacking_Auto.py

REM Pause for 5 seconds
timeout /t 5 /nobreak

REM Execute the second Python script
python Run_After_DLLHijacking_Auto.py

REM Pause to keep the window open
pause
