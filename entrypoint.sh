#!/bin/bash

function start_haproxy {
  echo -e "\n * Starting HAProxy"
  haproxy -p /var/run/haproxy.pid -f haproxy.cfg
  echo -e "   ...done.\n"
}

python3 gen_conf.py
cat haproxy.cfg
start_haproxy

# TODO Control HAProxy PIDs
bash --login -i
