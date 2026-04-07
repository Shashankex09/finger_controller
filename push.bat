@echo off
if "%~1"=="" (
    echo Usage: push.bat "Your commit message"
    exit /b 1
)
git add .
git commit -m "%*"
git push
echo Successfully pushed with message: %*
pause