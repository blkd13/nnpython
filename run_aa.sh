#!/bin/sh
while true; 
do
  logfile=./log/cc$(date +%Y%m%d).log
  # python aa.py >> ${logfile} 2>&1;
  python cc_exec.py >> ${logfile} 2>&1;
  date         >> ${logfile} 2>&1;
  sleep 40;
done
