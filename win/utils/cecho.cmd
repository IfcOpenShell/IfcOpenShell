:: Usage: call cecho.cmd background foreground "message here"
:: NOTES/TODOS 1) This is super slow 2) leading spaces are omitted 3) printing string with quotes doesn't work (quotes must be escaped awkwardly)
@powershell -command write-host -background %~1 -foreground "%~2" "%3"
@exit /b
