@echo off
setlocal ENABLEDELAYEDEXPANSION

rem ==========================================================
rem cecho.cmd - Fast ANSI color echo for Windows 10+
rem Emulates PowerShell escape codes like `t and `n
rem Usage: call cecho.cmd <bg> <fg> "Message"
rem ==========================================================

for /F %%A in ('echo prompt $E ^| cmd') do set "ESC=%%A"

set "BG=%~1"
set "FG=%~2"
set "TEXT=%~3"

rem Replace PowerShell-style escapes with real characters
set "TEXT=%TEXT:`t=	%"
set "TEXT=%TEXT:`"="%"

rem Foreground color table (0–15)
set "FGCOLOR[0]=30" & set "FGCOLOR[1]=34" & set "FGCOLOR[2]=32" & set "FGCOLOR[3]=36"
set "FGCOLOR[4]=31" & set "FGCOLOR[5]=35" & set "FGCOLOR[6]=33" & set "FGCOLOR[7]=37"
set "FGCOLOR[8]=90" & set "FGCOLOR[9]=94" & set "FGCOLOR[10]=92" & set "FGCOLOR[11]=96"
set "FGCOLOR[12]=91" & set "FGCOLOR[13]=95" & set "FGCOLOR[14]=93" & set "FGCOLOR[15]=97"

rem Background color table (0–7)
set "BGCOLOR[0]=40" & set "BGCOLOR[1]=44" & set "BGCOLOR[2]=42" & set "BGCOLOR[3]=46"
set "BGCOLOR[4]=41" & set "BGCOLOR[5]=45" & set "BGCOLOR[6]=43" & set "BGCOLOR[7]=47"

set "FGC=!FGCOLOR[%FG%]!"
set "BGC=!BGCOLOR[%BG%]!"

if defined BGC (
    set "STYLE=!ESC![!BGC!;!FGC!m"
) else (
    set "STYLE=!ESC![!FGC!m"
)

echo|set /p="!STYLE!!TEXT!!ESC![0m"
echo.
endlocal
exit /b 0
