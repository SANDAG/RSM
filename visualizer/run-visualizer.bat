@echo on

:: set paths

SET SIMWRAPPER_PATH=C:\projects\SimWrapper\test\visualizer\SimWrapper

cd /d %SIMWRAPPER_PATH%

:: use this to start simwrapper
:: and then type "http://localhost:8050/live" in a browser
simwrapper here

:: this starts the simwrapper and then opens the browser too. 
simwrapper open asim


