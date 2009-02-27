@echo off

if exist %~dp0\bin\peach.exe %~dp0\bin\peach.exe --strategy=rand.RandomMutationStrategy %1 %2 %3 %4 %5 %6 %7 %8 %9
if not exist %~dp0\bin\peach.exe python %~dp0\peach.py --strategy=rand.RandomMutationStrategy %1 %2 %3 %4 %5 %6 %7 %8 %9

