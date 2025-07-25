@echo off
set BACKUP_DIR=C:\Backups
set SOURCE_DIR=C:\ImportantFiles
set DATE=%date:~-4%-%date:~-7,2%-%date:~-10,2%

mkdir "%BACKUP_DIR%" 2>nul
robocopy "%SOURCE_DIR%" "%BACKUP_DIR%\%DATE%" /MIR /R:1 /W:1 /NP /LOG:"%BACKUP_DIR%\backup_log.txt"