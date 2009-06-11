@echo off

rem Build the binary version of Peach using py2exe
rem Copyright (c) Michael Eddington

cd c:\peach\tools

copy /y setup.py ..

cd c:\peach

rmdir /s/q bin
rmdir /s/q build
rmdir /s/q dist

rem -O0 will cause optmized byte code to
rem be generated
python -OO setup.py py2exe

ren dist bin
rmdir /s/q build
del /q setup.py

rem Build DbgProxyEvent
cd c:\peach\dependencies\src\peach-PyDbgEng
rmdir /s/q build dist
python py2exe\setup.py py2exe
copy /y dist\* c:\peach\bin
cd c:\peach

rem Extra re-dist files
copy C:\Python25\lib\site-packages\wx-2.8-msw-ansi\wx\gdiplus.dll bin
copy C:\Python25\lib\site-packages\wx-2.8-msw-ansi\wx\MSVCP71.dll bin
copy c:\windows\system32\MFC71.DLL bin
copy c:\windows\SysWOW64\mfc71.dll bin

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
