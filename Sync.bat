@echo off

echo Sync files to git
set /p commit_message= Enter commit message:
echo CommitMessage is: %commit_message%

git pull
git add .
git commit -m "%commit_message%"
git push

pause