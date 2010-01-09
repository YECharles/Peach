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
copy C:\Python26\Share\4Suite\default.cat build\bdist.win-amd64-2.6\msi\Share\4Suite
copy C:\Python26\Share\4Suite\Schemata\*.* build\bdist.win-amd64-2.6\msi\Share\4Suite\Schemata

rem -O0 will cause optmized byte code to
rem be generated
c:\python26\python -OO setup64.py py2exe

ren dist bin
rmdir /s/q build
del /q setup.py

rem Build DbgProxyEvent
rem cd c:\peach\dependencies\src\peach-PyDbgEng
rem rmdir /s/q build dist
rem python py2exe\setup.py py2exe
rem copy /y dist\* c:\peach\bin
rem cd c:\peach

rem These extra files not needed on x64 yet
rem Extra re-dist files
rem copy C:\Python25\lib\site-packages\wx-2.8-msw-ansi\wx\gdiplus.dll bin
rem copy C:\Python25\lib\site-packages\wx-2.8-msw-ansi\wx\MSVCP71.dll bin
rem copy c:\windows\system32\MFC71.DLL bin
rem copy c:\windows\SysWOW64\mfc71.dll bin
del /q bin\iphlpapi.dll

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
