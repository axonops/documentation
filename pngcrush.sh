#!/bin/bash

# This script runs pngcrush with its default settings against every PNG file in the repository
# It assumes pngcrush is installed in your path

cd $(dirname "${BASH_SOURCE[0]}")

find . -name '*.png' | while read F; do
	TMPF="$F-c.png"
	pngcrush "$F" "$TMPF"
	mv -v "$TMPF" "$F"
done
