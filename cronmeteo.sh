#!/bin/bash
if [ -f cronmeteo.config.sh ]; then
	source cronmeteo.config.sh
fi

if [ "$STARMETEO_AREA" == "" ]; then
	>&2 echo "ERROR : Check config file cronmeteo.config.sh"
	exit -1
fi

# add the bin/ dir into the path, so we are sure the rpitx and starmeteo exe are accessibles
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PATH=$PATH:$SCRIPT_DIR/bin

## Save forcast in a tmp file
python3 sm_forecast.py --backend $STARMETEO_BACKEND --latlong $STARMETEO_LATLONG --days 5 --output json > $STARMETEO_TMP
## Generate a readable forcast
python3 sm_forecast.py --backend file $STARMETEO_TMP --days 5 --output txt
## Generate forcast for starmeteo
prev=$(python3 sm_forecast.py --backend file $STARMETEO_TMP --output starmeteo)
sm_format=$(starmeteo $prev -areaid:$STARMETEO_AREA -quiet -rpitx)
echo -n "$sm_format" | sudo ./pocsag -f "$STARMETEO_FREQ" -r 1200 -t 1 2>/dev/null
sleep 4
# Time sync
echo "Time sync on $(date)"
curtime=$(starmeteo -time -areas:$STARMETEO_AREA -quiet -rpitx)
echo " curtime=$curtime"
echo -n "$curtime" | sudo ./pocsag -f "$STARMETEO_FREQ" -r 1200 -t 1 2>/dev/null
sleep 4

# Forcast again
echo " forecast=$sm_format"
echo -n "$sm_format" | sudo ./pocsag -f "$STARMETEO_FREQ" -r 1200 -t 1 2>/dev/null
sleep 4
echo -n "$sm_format" | sudo ./pocsag -f "$STARMETEO_FREQ" -r 1200 -t 1 2>/dev/null

