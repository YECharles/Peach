#!/bin/sh

BASEDIR=`dirname $0`
python $BASEDIR/peach.py --strategy=rand.RandomMutationStrategy $1 $2 $3 $4 $5 $6 $7 $8 $9

