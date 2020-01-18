#!/bin/bash

server_host=$1
server_port=$2
sleep_seconds=2

while true; do
    echo -n "Checking $server_host status... "

    output="$(nc -zv $server_host $server_port; echo $?)"

    echo "$output"

    if [[ $output == 0 ]]
    then
        echo "$server_host is running and ready to process requests."
        break
    fi

    echo "$server_host is warming up. Trying again in $sleep_seconds seconds..."
    sleep $sleep_seconds
done