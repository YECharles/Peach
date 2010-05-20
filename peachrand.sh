#!/bin/sh

BASEDIR=`dirname $0`
if [ ${#BASEDIR} == 0 ]
    then python peach.py --strategy=rand.RandomMutationStrategy $1 $2 $3 $4 $5 $6 $7 $8 $9
    else python $BASEDIR/peach.py --strategy=rand.RandomMutationStrategy $1 $2 $3 $4 $5 $6 $7 $8 $9
fi


