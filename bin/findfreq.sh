#!/bin/bash

STEP=1000
DEFAULT_FREQ=466220000

read -p "Enter frequency [$DEFAULT_FREQ] : " freq
freq=${freq:-$DEFAULT_FREQ}

while true; do
    echo -n "Freq=$freq . ← decrease | → increase | Q quit: "

    # Read first character
    IFS= read -rsn1 key

    # Arrow keys start with ESC
    if [[ $key == $'\e' ]]; then
        IFS= read -rsn2 key2
        key+="$key2"
    fi

    echo

    case "$key" in
        $'\e[D') ((freq -= STEP)) ;;   # Left arrow
        $'\e[C') ((freq += STEP)) ;;   # Right arrow
		"") ;; # replay freq
        q|Q)      exit 0 ;;
        *)        continue ;;
    esac

    echo "Frequency: $freq"
    printf "25176:HELLOWORLD" | sudo pocsag -f "$freq" -t 1
done