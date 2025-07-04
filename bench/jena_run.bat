@echo off
setlocal

set "FUSEKI_HOME=C:\Program Files\apache-jena-fuseki-5.4.0"
set "FUSEKI_BASE=C:\fuseki-data"

if not exist "%FUSEKI_BASE%" (
    mkdir "%FUSEKI_BASE%"
)

pushd "%FUSEKI_HOME%"
call fuseki-server.bat --base="%FUSEKI_BASE%"
popd
