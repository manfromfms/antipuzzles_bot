@echo off
if "%1"=="" goto NoFile
python your_script.py %1
goto End

:NoFile
echo Please drag and drop a file onto this batch file.
pause
exit /b 1

:End
exit /b 0