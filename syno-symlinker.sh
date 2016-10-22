#!/bin/sh

#symlinks packages to /bin/

#git
ln -s /volume1/\@appstore/git/bin/git /bin/git

#nano
ln -s /volume1/\@appstore/nano/bin/nano /bin/nano

#mc
ln -s /volume1/\@appstore/mc/bin/mc /bin/mc

#transmission-remote
ln -s /volume1/\@appstore/transmission/bin/transmission-remote /bin/transmission-remote

#pip3.5 (pyhton 3.5)
ln -s /volume1/\@appstore/py3k/usr/local/bin/pip3.5 /bin/pip3.5

#youtube-dl (python 3.5)
ln -s /volume1/\@appstore/py3k/usr/local/bin/youtube-dl /bin/youtube-dl

#ffprobe
ln -s /volume1/\@appstore/ffmpeg/bin/ffprobe /bin/ffprobe