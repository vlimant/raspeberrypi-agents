#!/bin/bash
echo $1 is the IP we are starting on
sleep 2

echo starting the workload emulator
python /home/vlimant/cherrypy/working.py $1 &
sleep 2

echo starting the web service
python /home/vlimant/cherrypy/run_cherrypy.py
