;
; Peach 2.3 Installer
;
; Copyright (c) 2007-2009 Michael Eddington
;
; Permission is hereby granted, free of charge, to any person obtaining a copy 
; of this software and associated documentation files (the "Software"), to deal
; in the Software without restriction, including without limitation the rights 
; to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
; copies of the Software, and to permit persons to whom the Software is 
; furnished to do so, subject to the following conditions:
;
; The above copyright notice and this permission notice shall be included in	
; all copies or substantial portions of the Software.
;
; THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
; IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
; FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
; AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
; LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
; OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
; SOFTWARE.
;
; Authors:
;   Michael Eddington (mike@phed.org)
;
; $Id$
;

;--------------------------------
;Include Modern UI

  !include "MUI.nsh"

;--------------------------------
;General

  ;Name and file
  Name "Peach 2.3 Beta 2"
  OutFile "Peach-2.3-BETA2-py25.exe"

  ;Default installation folder
  InstallDir "c:\peach"
  
  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\Peach" ""

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

;  !insertmacro MUI_PAGE_LICENSE "${NSISDIR}\Docs\Modern UI\License.txt"
;  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Dummy Section" SecDummy
  
  SetOutPath "$INSTDIR"
  
  ; Detecting ActiveState python 2.5
  StrCpy $0 0
loop:
  EnumRegKey $1 HKLM SOFTWARE\ActiveState\ActivePython 0
  StrCmp $1 "" done
  StrCpy $2 $1 3
  StrCmp $2 "2.5" ok loop
done:
    MessageBox MB_YESNO|MB_ICONSTOP "Could not locate ActivePython v2.5 32bit.  Install anyways?" IDYES ok IDNO 0
      Abort "Requires ActivePython v2.5 32bit"
ok:
    
  ; HKLM/SOFTWARE/ActiveState/2.5.n.n (defualt) == install folder
  ; installfolder/python.exe.manifest (processorArchitecture="X86")
  
  ; Detecting winpcap is installed
  ; HKLM/SOFTWARE/Microsoft/Windows/CurrentVersion/Uninstall/WinPcapInst:VersionMajor == 4
  
  ;ADD YOUR OWN FILES HERE...
  File /r /x docs /x "dependencies" /x ".svn" /x "*.ncb" /x "*.ncb" /x "obj" /x "bin" /x "Peach-2*.exe" /x "logtest" /x "*.pyc" /x "tools\www" "c:\peach\*.*"
  File /r /x ".svn" /x "src" /x "py2.4-win64" /x "py2.6-*" /x "osx-10.5" "c:\peach\dependencies"
  
  CreateDirectory "$SMPROGRAMS\Peach"
  CreateShortCut "$SMPROGRAMS\Peach\Peach Documentation.lnk" "$INSTDIR\readme.html" "" "$INSTDIR\Peach\Gui\icons\peach20x20.ico"
  CreateShortCut "$SMPROGRAMS\Peach\Peach Builder.lnk" "$INSTDIR\PeachBuilder.pyw" "" "$INSTDIR\Peach\Gui\icons\peach20x20.ico"
  CreateShortCut "$SMPROGRAMS\Peach\Peach Validation.lnk" "$INSTDIR\peachvalidator.pyw" "" "$INSTDIR\Peach\Gui\icons\peach20x20.ico"
  CreateShortCut "$SMPROGRAMS\Peach\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  
  ; Execute dependencies
  
  ; have msi now
  ExecWait "msiexec /qn /i $INSTDIR\dependencies\py2.5-win32\4Suite-XML-1.0.2.win32-py2.5.msi"
  ExecWait "msiexec /qn /i $INSTDIR\dependencies\py2.5-win32\cDeepCopy-0.2.win32-py2.5.msi"
  ExecWait "msiexec /qn /i $INSTDIR\dependencies\py2.5-win32\comtypes-0.4.2.win32-py2.5.msi"
  ExecWait "msiexec /qn /i $INSTDIR\dependencies\py2.5-win32\cPeach-0.2.win32-py2.5.msi"
  ExecWait "msiexec /qn /i $INSTDIR\dependencies\py2.5-win32\pyasn1-0.0.7a.win32-py2.5.msi"
  ExecWait "msiexec /qn /i $INSTDIR\dependencies\py2.5-win32\pyvmware-0.1.win32-py2.5.msi"
  ExecWait "msiexec /qn /i $INSTDIR\dependencies\py2.5-win32\pcap-peach.win32-py2.5.msi"
  ExecWait "msiexec /qn /i $INSTDIR\dependencies\py2.5-win32\PyDbgEng-0.9.win32-py2.5.msi"
  ExecWait "msiexec /qn /i $INSTDIR\dependencies\py2.5-win32\zope.interface-3.3.0.win32-py2.5.msi"
  ExecWait "msiexec /qn /i $INSTDIR\dependencies\py2.5-win32\Twisted-8.0.1.win32-py2.5.msi"
  
  ; Not sure if we can get msi's of these
  ExecWait "$INSTDIR\dependencies\win32\wxPython2.8-win32-ansi-2.8.7.1-py25.exe"

  ; This should be after wxPython
  ExecWait "msiexec /qn /i $INSTDIR\dependencies\win32\wxPropertyGrid-1.2.11.win32-py2.5.msi"

  ;Store installation folder
  WriteRegStr HKCU "Software\Peach" "" $INSTDIR
  
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ; Only install WinPcap if not already installed!
  ; Also, do this as last item since we may need a reboot!
  ClearErrors
  ReadRegStr $0 HKLM SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\WinPcapInst "VersionMajor"
  StrCmp $0 '' 0 skipwinpcap
    ExecWait "$INSTDIR\dependencies\win32\WinPcap_4_0_2.exe" ; might need reboot?
skipwinpcap:

    ; Lets compile down Peach
    ExecWait 'python $INSTDIR\tools\compilepeach.py "$INSTDIR" '

SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecDummy ${LANG_ENGLISH} "A test section."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDummy} $(DESC_SecDummy)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;ADD YOUR OWN FILES HERE...
  
  Delete "$INSTDIR\Uninstall.exe"

  ; Remove it all baby!!!
  RMDir /r "$INSTDIR"
  RMDir /r "$SMPROGRAMS\Peach"

  DeleteRegKey /ifempty HKCU "Software\Peach"

SectionEnd

; end
