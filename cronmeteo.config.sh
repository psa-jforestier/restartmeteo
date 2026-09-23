# French departement number
export STARMETEO_AREA=75

# Your latitude and longitude coordinate
export STARMETEO_LATLONG=48.8529,2.3445

###############
# Change this only if you know what your are doing :
###############

# POCSAG frequency in Hz
export STARMETEO_FREQ=466205000

# A temp file (can be a RAM drive to prevent SD card consumption)
export STARMETEO_TMP=/tmp.ram/prev.json

# The backend for weather forecast. Default is "openmeteo"
# can be : "weatherunderground --wu-api=1234"
export STARMETEO_BACKEND=openmeteo

