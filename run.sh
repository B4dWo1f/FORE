#!/bin/bash

# Backup previous station information
cp $HOME/CODES/FORE/stations.csv $HOME/CODES/FORE/stations.csv.old

# Download data
$HOME/CODES/FORE/spider.py > $HOME/spider.log 2>> $HOME/spider.log

# Fix data (correct duplicates, etc)
$HOME/CODES/FORE/process.py 2> /dev/null

# collect all the station information available
cat $HOME/CODES/FORE/stations.csv $HOME/CODES/FORE/stations.csv.old | sort | uniq > $HOME/CODES/FORE/stations.csv.1

# Clean
mv $HOME/CODES/FORE/stations.csv $HOME/CODES/FORE/stations.csv.old
mv $HOME/CODES/FORE/stations.csv.1 $HOME/CODES/FORE/stations.csv


#### Old cron-job
#31 */2 * * * cp $HOME/CODES/FORE/stations.csv $HOME/CODES/FORE/stations.csv.old && $HOME/CODES/FORE/spider.py > $HOME/spider.log && $HOME/CODES/FORE/process.py 2> /dev/null

