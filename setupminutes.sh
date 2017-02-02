#!/bin/bash
if [[ $1 == "" ]];then
    echo error in params
    exit 255
fi
rm -f $2
ln -s $1 $2
notify-send Notebox "Minutes Links created!"
exit 0
