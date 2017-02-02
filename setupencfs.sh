#!/bin/bash
if [[ $1 == "" ]];then
    echo error in params
    echo $0 '<Location of Private folder> <location for notebox link>'
    exit 255
fi
rm -f $2
ln -s $1 $2
notify-send Notebox "ENCFS Links created!"
exit 0
