#!/bin/bash

rm plugin.audio.bandcamp-$1.zip

mkdir plugin.audio.bandcamp
mkdir plugin.audio.bandcamp/resources
mkdir plugin.audio.bandcamp/resources/data
mkdir plugin.audio.bandcamp/resources/language
mkdir plugin.audio.bandcamp/resources/language/English
mkdir plugin.audio.bandcamp/resources/lib
mkdir plugin.audio.bandcamp/resources/media

cp LICENSE.txt README.md default.py addon.xml changelog.txt icon.png plugin.audio.bandcamp
mv plugin.audio.bandcamp/README.md plugin.audio.bandcamp/README
cp resources/__init__.py resources/settings.xml plugin.audio.bandcamp/resources/
cp resources/data/key.txt plugin.audio.bandcamp/resources/data
cp resources/language/English/strings.xml plugin.audio.bandcamp/resources/language/English
cp resources/lib/__init__.py resources/lib/bandcamp.py plugin.audio.bandcamp/resources/lib

zip -r plugin.audio.bandcamp-$1.zip plugin.audio.bandcamp

rm -r plugin.audio.bandcamp
