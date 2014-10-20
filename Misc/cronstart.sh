#!/bin/sh

#If the process has a parent it goes here. Like mono or python
PARENT_PROCESS="mono"
PROCESS="/Users/TestApp/TestApp/bin/Debug/TestApp.exe"

#Find the process in the ps list while ignoring the grep process itself
PROC=`ps aux | grep "$PARENT_PROCESS $PROCESS" | grep -v "grep"`

if [ "$PROC" == "" ]; then
  #No process found
  echo "Process not started. Starting..."
  $PARENT_PROCESS $PROCESS &
else
  #Process found
  echo "Process already started"
fi

echo "Done"
