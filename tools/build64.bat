@echo off

rem Build the binary version of Peach using py2exe
rem Copyright (c) Michael Eddington

cd c:\peach\tools

copy /y setup64.py ..

cd c:\peach

rmdir /s/q bin
rmdir /s/q build
rmdir /s/q dist

mkdir build\bdist.win-amd64-2.6\msi\Share\4Suite\Schemata
copy C:\Python27\Share\4Suite\default.cat build\bdist.win-amd64-2.6\msi\Share\4Suite
copy C:\Python27\Share\4Suite\Schemata\*.* build\bdist.win-amd64-2.6\msi\Share\4Suite\Schemata

rem -O0 will cause optmized byte code to be generated
c:\python27\python -OO setup64.py py2exe

ren dist bin
rmdir /s/q build
del /q setup.py

rem Extra re-dist files
copy C:\Python27\lib\site-packages\wx-2.8-msw-ansi\wx\gdiplus.dll bin
copy C:\Python27\lib\site-packages\wx-2.8-msw-ansi\wx\MSVCP71.dll bin
copy c:\windows\system32\MFC71.DLL bin
copy c:\windows\SysWOW64\mfc71.dll bin
del /q bin\iphlpapi.dll
copy tools\bangexploitable\x64\msec.dll bin

xcopy /s/q c:\peach\Peach\Generators\xmltests c:\peach\bin\xmltests\

if "%1"==all call c:\peach\tools\gendocs.bat
if "%1"==bin goto BINONLY

goto EXIT

:BINONLY

cd c:\peach
copy /y C:\peach\Peach\Engine\PeachTypes.xml
rmdir /s/q dependencies
rmdir /s/q Peach
rmdir /s/q test
del /y *.py
del /y *.pyw

:EXIT

rem ALl done!
