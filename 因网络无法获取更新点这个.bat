@echo off
if exist "%SystemRoot%\SysWOW64" path %path%;%windir%\SysNative;%SystemRoot%\SysWOW64;%~dp0
bcdedit >nul
if '%errorlevel%' NEQ '0' (goto UACPrompt) else (goto UACAdmin)
:UACPrompt
%1 start "" mshta vbscript:createobject("shell.application").shellexecute("""%~0""","::",,"runas",1)(window.close)&exit
exit /B
:UACAdmin
chcp 65001 >nul 2>&1
cd /d "%~dp0"
echo **************************************************************
echo *                  修复网络工具--hosts方式                   *
echo **************************************************************
echo *                 项目名称：Pycatmv                          *
echo **************************************************************
echo #

set load=0
findstr "185.199.108.133" C:\Windows\System32\drivers\etc\hosts >nul 2>&1 && set load=1
findstr "185.199.109.133" C:\Windows\System32\drivers\etc\hosts >nul 2>&1 && set load=1
findstr "185.199.110.133" C:\Windows\System32\drivers\etc\hosts >nul 2>&1 && set load=1
findstr "185.199.111.133" C:\Windows\System32\drivers\etc\hosts >nul 2>&1 && set load=1
findstr "151.101.100.133" C:\Windows\System32\drivers\etc\hosts >nul 2>&1 && set load=1
ipconfig /flushdns >nul 2>&1
if %load%==1 (echo * 请不要重复运行喔 && pause && exit)
echo # 正在修复中......
echo 185.199.108.133 raw.githubusercontent.com>>C:\Windows\System32\drivers\etc\hosts
echo 185.199.109.133 raw.githubusercontent.com>>C:\Windows\System32\drivers\etc\hosts
echo 185.199.110.133 raw.githubusercontent.com>>C:\Windows\System32\drivers\etc\hosts
echo 185.199.111.133 raw.githubusercontent.com>>C:\Windows\System32\drivers\etc\hosts
echo 151.101.100.133 raw.githubusercontent.com>>C:\Windows\System32\drivers\etc\hosts
ipconfig /flushdns >nul 2>&1
echo * 修复完成！！
pause