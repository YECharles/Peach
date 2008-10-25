@echo off

cd DbgEngTlb
nmake clean all || goto error
cd ..

cd DbgEventProxy
set INCLUDE=%INCLUDE%;"c:\Program Files\Microsoft Platform SDK for Windows Server 2003 R2\Include\atl\"
set INCLUDE=%INCLUDE%;"c:\Program Files\Microsoft Platform SDK for Windows Server 2003 R2\Include\mfc\"
vcbuild /rebuild /useenv DbgEventProxy.sln "Release|Win32"  || goto error
cd ..

echo "*** build success ***"
goto end

:error
echo "*** build failed ***"

:end

