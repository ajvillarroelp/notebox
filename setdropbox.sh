#!/bin/bash
cd ~/.notebox
DROPBOXDIR=$(cat ~/.notebox/notebox.conf | grep DROPBOXDIR | cut -d= -f 2)
if [ ! -d $DROPBOXDIR/Apps/notebox ];then
	echo Creating Notebox directory in Dropbox App dir 
	mkdir $DROPBOXDIR/Apps/notebox
	cp -rp notes $DROPBOXDIR/Apps/notebox/
	if [ $? -eq 0 ];then
		rm -rf notes
		ln -s $DROPBOXDIR/Apps/notebox/notes notes
	else
		echo "Error copying notes to Dropbox dir! $DROPBOXDIR/Apps/notebox/"
		exit 2
	fi
	cp notebox.dat $DROPBOXDIR/Apps/notebox
else
	echo Found notebox directory in Dropbox!
	echo Not copying local data 
fi
cat  ~/.notebox/notebox.conf | grep -v NOTEDB > /tmp/notebox.conf
echo "NOTEDB=$DROPBOXDIR/Apps/notebox/notebox.dat" >>/tmp/notebox.conf
cp /tmp/notebox.conf ~/.notebox/notebox.conf
