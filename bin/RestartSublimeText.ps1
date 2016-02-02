"Restarting Sublime Text..."
start-sleep -milliseconds 500
stop-process -name sublime_text -erroraction silentlycontinue
start-sleep -milliseconds 250
& subl.exe
