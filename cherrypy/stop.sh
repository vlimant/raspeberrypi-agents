#!/bin/bash
echo killing existing instances
kill -9 `ps -e -f | grep cherr | grep python | awk '{print $2}'`
kill -9 `ps -e -f | grep working.py | grep python | awk '{print $2}'`
