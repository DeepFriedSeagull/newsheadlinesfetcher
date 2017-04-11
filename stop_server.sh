#!/bin/bash
kill -9 $(ps aux | grep '[f]lask run'| awk '{print $2}')
kill -9 $(ps aux | grep '[m]ongod --config ./mongod.conf'| awk '{print $2}')
