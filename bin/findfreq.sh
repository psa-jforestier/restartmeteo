#!/bin/bash

STEP=1000
DEFAULT_FREQ=466220000

read -p "Enter frequency [$DEFAULT_FREQ] : " freq
freq=${freq:-$DEFAULT_FREQ}

while true; do
    read -n1 -p "Freq=$freq . Press P for plus, M for minus (Q to quit): " key
    echo

    case "${key^^}" in
        P) ((freq += STEP)) ;;
        M) ((freq -= STEP)) ;;
        Q) exit 0 ;;
	"")
	  ;;
        *) continue ;;
    esac

    echo "Frequency: $freq"
    printf "25176:HELLOWORLD" | sudo pocsag -f $freq -t 1
done
