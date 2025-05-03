@echo off
setlocal enabledelayedexpansion

:: Get the absolute path of the dragged file
set "filePath=%~f1"

:: Get the directory of the batch file
set "batchDir=%~dp0"

:: Activate the virtual environment
call "%batchDir%\venv\Scripts\activate"

:: Change the directory to the location of main.py
cd /d "%batchDir%"

:: Start the main.py Python file and provide it with the absolute path of the file
python "generator.py" "%filePath%"

pause