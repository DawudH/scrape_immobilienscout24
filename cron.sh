#!/bin/bash

cd ~/scrape_immobilienscout24/
PATH=$PATH:/usr/local/bin
export PATH

# Log rotation
LOG_DIR=~/scrape_immobilienscout24/log
LOG="${LOG_DIR}/LOG.log"

LogRotate () {
local f="$1"
local limit=$2
# Deletes old log file
if [ -f $f ] ; then
CNT=${limit}
let P_CNT=CNT-1
if [ -f ${f}.${limit} ] ; then
rm ${f}.${limit}
fi

# Renames logs .1 trough .4
while [[ $CNT -ne 1 ]] ; do
if [ -f ${f}.${P_CNT} ] ; then
mv ${f}.${P_CNT} ${f}.${CNT}
fi
let CNT=CNT-1
let P_CNT=P_CNT-1
done

# Renames current log to .1
mv $f ${f}.1
fi
}

TODAY=$(date)
echo "-----------------------------------------------------" > $LOG
echo "Date: $TODAY" >> $LOG
echo "-----------------------------------------------------" >> $LOG

(scrapy crawl ImmobilienSpider 2>&1)>> $LOG

LogRotate $LOG 6



