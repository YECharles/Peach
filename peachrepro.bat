@echo off

if exist %~dp0\bin\peach.exe %~dp0\bin\peach.exe --strategy=sequencial.ReproStrategy %1 %2 %3 %4 %5 %6 %7 %8 %9
if not exist %~dp0\bin\peach.exe python %~dp0\peach.py --strategy=sequencial.ReproStrategy %1 %2 %3 %4 %5 %6 %7 %8 %9

