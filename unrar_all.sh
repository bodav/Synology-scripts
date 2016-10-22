#!/bin/sh

######################
# Extract rar script #
######################

# Needs findutils package
# ipkg install findutils

# Find all .rar files i dir+subdirs and extracts
# (-o- argument) - Don't overwrite already extracted files

/opt/bin/find /volume1/somedir/ -type f -iname '*.rar' -execdir unrar e -o- {} \;
