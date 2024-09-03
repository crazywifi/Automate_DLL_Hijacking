@echo off
REM Change to the directory of the batch file
cd /d %~dp0


REM Execute the second Python script
python Run_After_DLLHijacking_Auto.py

REM Pause to keep the window open
pause
