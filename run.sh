#!/bin/bash
BASEDIR=$(dirname "$0")

# Backup previous station information
cp $BASEDIR/stations.csv $BASEDIR/stations.csv.old

# Download data
$BASEDIR/spider.py >> $HOME/spider.out 2>> $HOME/spider.err

## Fix data (correct duplicates, etc)  # Unnecessary after the pandas update
#$BASEDIR/process.py 2> /dev/null      # to be removed

# collect all the station information available
cat $BASEDIR/stations.csv $BASEDIR/stations.csv.old | sort | uniq > $BASEDIR/stations.csv.1

# Clean
mv $BASEDIR/stations.csv $BASEDIR/stations.csv.old
mv $BASEDIR/stations.csv.1 $BASEDIR/stations.csv

## Desktop notification
#notify-send "Weather data retrieved"
