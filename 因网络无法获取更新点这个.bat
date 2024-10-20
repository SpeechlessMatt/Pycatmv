@echo off
if exist "%SystemRoot%\SysWOW64" path %path%;%windir%\SysNative;%SystemRoot%\SysWOW64;%~dp0
bcdedit >nul
if '%errorlevel%' NEQ '0' (goto UACPrompt) else (goto UACAdmin)
:UACPrompt
%1 start "" mshta vbscript:createobject("shell.application").shellexecute("""%~0""","::",,"runas",1)(window.close)&exit
exit /B
:UACAdmin
cd /d "%~dp0"
echo 已获取管理员权限
echo **************************************************************
echo *本项目在GitHub上开源，绝不收集任何您的信息，只提供服务  *
echo **************************************************************
echo *                         项目名为：Pycatmv                                              *
echo **************************************************************
echo #
echo # 正在为你添加DNS解析，帮助你从Github上获取更新...
echo #
set load=0
findstr "185.199.108.133" C:\Windows\System32\drivers\etc\hosts >nul 2>&1 && set load=1
findstr "185.199.109.133" C:\Windows\System32\drivers\etc\hosts >nul 2>&1 && set load=1
findstr "185.199.110.133" C:\Windows\System32\drivers\etc\hosts >nul 2>&1 && set load=1
findstr "185.199.111.133" C:\Windows\System32\drivers\etc\hosts >nul 2>&1 && set load=1
if %load%==1 (echo * 你已经运行过该脚本了，不要重复运行哦 && pause && exit)
echo 185.199.108.133 raw.githubusercontent.com>>C:\Windows\System32\drivers\etc\hosts
echo 185.199.109.133 raw.githubusercontent.com>>C:\Windows\System32\drivers\etc\hosts
echo 185.199.110.133 raw.githubusercontent.com>>C:\Windows\System32\drivers\etc\hosts
echo 185.199.111.133 raw.githubusercontent.com>>C:\Windows\System32\drivers\etc\hosts
echo * 成功啦！
pause