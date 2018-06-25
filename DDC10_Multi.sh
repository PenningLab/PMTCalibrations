#!/bin/sh
if [ $# -lt 2 ]
then
 echo "Missing arguments!!! To run"
 echo "sh DDC10_Multi.sh [filename] [# files] <starting index>"
 return 
fi
filename=$1
num=$2
init=0
if [ $# -eq 3 ]
then
 init=$3
 num=`expr ${init} + ${num}`
fi

for j in `seq ${init} ${num}`
do
 echo "starting file ${j}"
 DDC10_BinWaveCap_ChSel 0x1 8192 18000 /mnt/share/${filename}/${j}.bin >> /mnt/share/${filename}/${j}.log
 echo "file ${j} complete"
done

