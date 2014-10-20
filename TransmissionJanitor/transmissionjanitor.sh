#!/bin/sh
#Created 2014-08-11
#Script to clear all completed torrents from transmission, using transmission-remote

#Transmission user / pass
USER=xxxx
PASS=xxxx

#Fullpath to transmission-remote executable
REMOTE="/usr/local/transmission/bin/transmission-remote -n $USER:$PASS"

TORRENTLIST=`$REMOTE --list | grep -Eo '^ *([0-9]+)'`

for TORRENTID in $TORRENTLIST
do
  echo "Processing torrent with ID ($TORRENTID)"
  DOWNLOADED=`$REMOTE --torrent $TORRENTID --info | grep "Percent Done: 100%"`

  if [ "$DOWNLOADED" != "" ]; then
    echo "Torrent is done. Removing."
    $REMOTE --torrent $TORRENTID --remove
  else
    echo "Torrent #$TORRENTID is not completed. Ignoring."
  fi
done

echo "Done!"
