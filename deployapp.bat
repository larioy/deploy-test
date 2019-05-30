@echo off
chcp 65001 >nul 2>nul
::APP配置信息
::APP代码的本地路径applocalpath
set applocalpath=D:\bluekingapp\code\vm-app
set bkhost=http://paas.canway.net
set appid=vm-app
set appname="虚拟机资源管理"
::APP简介introduction
set introduction="虚拟机资源管理"
set creater=iven

::SVN信息
::SVN路径，此路径下创建APP的SVN库
set svnpath=http://192.168.165.250/svn/community
set svnuser=iven
set svnpwd=1qw2#ER$

::PAAS数据库配置信息（open_paas和app数据库所在的数据库服务器凭据信息）
set paasdbhost=192.168.165.42
set paasdbuser=root
set paasdbpwd=TqcAtuef7G

rd /q /s %applocalpath%\.svn >nul 2>nul
rd /q /s %applocalpath%\.idea >nul 2>nul

::创建SVN库
set svnurl=%svnpath%/%appid%
"C:\Program Files\TortoiseSVN\bin\svn.exe" mkdir %svnurl% -m %appid% --username "%svnuser%" --password "%svnpwd%" >nul
CHOICE /T 10 /C ync /CS /D y /n >nul
rd /q /s %applocalpath%\.svn >nul 2>nul

::创建数据库
set proddb=%appid%
set testdb=%appid%-test
"C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe" -u root -h %paasdbhost% -p"%paasdbpwd%" -e "CREATE DATABASE `%testdb%` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;" >nul 2>nul
"C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe" -u root -h %paasdbhost% -p"%paasdbpwd%" -e "CREATE DATABASE `%proddb%` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;" >nul 2>nul


::创建APP修改APP配置文件
"C:\Python27\python.exe" .\createapp.py "%paasdbhost%" "%paasdbuser%" "%paasdbpwd%" "%appid%" "%appname%" "%introduction%" "%creater%" "%svnurl%" "%svnuser%" "%svnpwd%" "%bkhost%" "%applocalpath%"

::提交SVN代码
rd /q /s %applocalpath%\.svn >nul 2>nul
"C:\Program Files\TortoiseSVN\bin\svn.exe" checkout %svnurl% %applocalpath% --username "%svnuser%" --password "%svnpwd%" >nul 2>nul
"C:\Program Files\TortoiseSVN\bin\svn.exe" add %applocalpath%\* >nul 2>nul
"C:\Program Files\TortoiseSVN\bin\svn.exe" commit %applocalpath% -m "%appid%" >nul 2>nul
echo "success!"
pause