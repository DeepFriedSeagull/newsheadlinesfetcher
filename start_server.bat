rem Seting the codepage for the terminal 
chcp 65001

rem Starting MongoDB Server
set PATH=%PATH%;"C:\Program Files\MongoDB\Server\3.4\bin"
rem start mongod.exe --dbpath "%~dp0images_db"
start mongod.exe --dbpath "D:\work\mongodb"


rem Starting flask with our virtual environment
set FLASK_APP=newsheadlinesfetcher.py
set FLASK_DEBUG=1
%~dp0dev\Scripts\activate.bat & python -m flask run