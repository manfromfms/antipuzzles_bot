@echo off
if "%1"=="" goto NoFile
cd /d "%~dp0"
call ".venv\Scripts\activate"
python ./generate.py %1
goto End

:NoFile
echo Please drag and drop a file onto this batch file.
pause
exit /b 1

:End
pause
exit /b 0