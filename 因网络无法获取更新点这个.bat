@echo off
if exist "%SystemRoot%\SysWOW64" path %path%;%windir%\SysNative;%SystemRoot%\SysWOW64;%~dp0
bcdedit >nul
if '%errorlevel%' NEQ '0' (goto UACPrompt) else (goto UACAdmin)
:UACPrompt
%1 start "" mshta vbscript:createobject("shell.application").shellexecute("""%~0""","::",,"runas",1)(window.close)&exit
exit /B
:UACAdmin
cd /d "%~dp0"
echo �ѻ�ȡ����ԱȨ��
echo **************************************************************
echo *����Ŀ��GitHub�Ͽ�Դ�������ռ��κ�������Ϣ��ֻ�ṩ����  *
echo **************************************************************
echo *                         ��Ŀ��Ϊ��Pycatmv                                              *
echo **************************************************************
echo #
echo # ����Ϊ������DNS�������������Github�ϻ�ȡ����...
echo #
set load=0
findstr "185.199.108.133" C:\Windows\System32\drivers\etc\hosts >nul 2>&1 && set load=1
findstr "185.199.109.133" C:\Windows\System32\drivers\etc\hosts >nul 2>&1 && set load=1
findstr "185.199.110.133" C:\Windows\System32\drivers\etc\hosts >nul 2>&1 && set load=1
findstr "185.199.111.133" C:\Windows\System32\drivers\etc\hosts >nul 2>&1 && set load=1
ipconfig /flushdns
if %load%==1 (echo * ���Ѿ����й��ýű��ˣ���Ҫ�ظ�����Ŷ && pause && exit)
echo 185.199.108.133 raw.githubusercontent.com>>C:\Windows\System32\drivers\etc\hosts
echo 185.199.109.133 raw.githubusercontent.com>>C:\Windows\System32\drivers\etc\hosts
echo 185.199.110.133 raw.githubusercontent.com>>C:\Windows\System32\drivers\etc\hosts
echo 185.199.111.133 raw.githubusercontent.com>>C:\Windows\System32\drivers\etc\hosts
ipconfig /flushdns
echo * �ɹ�����
pause