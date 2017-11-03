#!/bin/bash
BASEDIR=$(dirname "$0")

# Backup previous station information
cp $BASEDIR/stations.csv $BASEDIR/stations.csv.old

# Download data
$BASEDIR/spider.py > $HOME/spider.log 2>> $HOME/spider.log

# Fix data (correct duplicates, etc)
$BASEDIR/process.py 2> /dev/null

# collect all the station information available
cat $BASEDIR/stations.csv $BASEDIR/stations.csv.old | sort | uniq > $BASEDIR/stations.csv.1

# Clean
mv $BASEDIR/stations.csv $BASEDIR/stations.csv.old
mv $BASEDIR/stations.csv.1 $BASEDIR/stations.csv


#### Old cron-job
#31 */2 * * * cp $HOME/CODES/FORE/stations.csv $HOME/CODES/FORE/stations.csv.old && $HOME/CODES/FORE/spider.py > $HOME/spider.log && $HOME/CODES/FORE/process.py 2> /dev/null

