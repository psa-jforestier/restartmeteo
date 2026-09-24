#!/usr/bin/env python3
'''
starmeteo reverse engeneering project

This tool generate a StarMeteo compatible message for weather forecast.
It can use different weather forcast backend.

For paris :
python sm_forecast.py --backend om --latlong 48.8534,2.3488
'''

import argparse
import requests
import math
import json
from sm_utils import *
from datetime import datetime, timedelta
from urllib.parse import urlencode

global VERBOSE
VERBOSE = False

def get_weatherunderground(v, location, latlong, apikey):
    if (latlong == location == None):
        error("You must provide a --location or a --latlong")
        quit(-3)
    if (latlong == None):
        debug(v, f"Geocoding location : {location} ...")
        geocode = wu_geocode_location(location, apikey)
        debug(v, f"Found location : {geocode}")
        lat, lon, tz, place_name = geocode
    else:
        lat, lon = map(float, latlong.split(","))
    debug(v, "Fetching forecast...")
    data = wu_fetch_5day(lat, lon, tz)
    
def wu_fetch_5day(lat, long, tz):
    # tz not used
    global VERBOSE
    # to be continued
def wu_geocode_location(location: str, apikey:str):
    url = f"https://api.weather.com/v3/location/search"
    r = requests.get(url, params={
        "apiKey": apikey, 
        "query": location, 
        "language": "en-US", 
        "format": "json"
        }, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not data.get("location"):
        raise RuntimeError(f"No geocoding results for {location!r}")
    lat = data["location"]["latitude"][0]
    lon = data["location"]["longitude"][0]
    return lat,lon, None, data["location"]["displayName"][0]
    
def om_geocode_city(city_name: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    r = requests.get(url, params={"name": city_name, "count": 1, "language": "en", "format": "json"}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not data.get("results"):
        raise RuntimeError(f"No geocoding results for {city_name!r}")
    best = data["results"][0]
    return best["latitude"], best["longitude"], best.get("timezone"), best.get("name")


def om_fetch_5day(lat: float, lon: float, timezone: str):

    global VERBOSE
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
        "forecast_days": 5,
        "timezone": timezone or "auto",
    }
    # // we get values starting from today's 03:00 for 6 days (including the current one)
    now = datetime.now()
    start_hour = now.replace(hour=3, minute=0, second=0, microsecond=0)
    end_hour = (start_hour + timedelta(days=5)).replace(hour=23, minute=59, second=59)
    params = {
        "latitude": lat,
        "longitude": lon,
        "temperature_unit": "celsius",
        "wind_speed_unit": "ms",
        "precipitation_unit": "mm",
        "timezone": timezone or "auto",
        "start_hour": start_hour.strftime("%Y-%m-%dT%H:%M:%S"),
        "end_hour": end_hour.strftime("%Y-%m-%dT%H:%M:%S"),
        "hourly": "temperature_2m_min,temperature_2m_max,cloud_cover,snowfall,precipitation_probability,rain,weather_code",
        "temporal_resolution": "hourly_6"
    }
    debug(VERBOSE, "URL   : " + url)
    debug(VERBOSE, "Param : " + urlencode(params))

    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
#    with open("data_om.json", "w", encoding="utf-8") as file:
#        json.dump(data, file, indent=2, ensure_ascii=False)
    return data


global WMO_CODE_LOOKUP
WMO_CODE_LOOKUP = {
    ## wmo_code => [ icone day, icon night, label ]
    0: [0x00, 0x18, "clear sky"],
    1: [0x01, 0x19, "mainly clear"],
    2: [0x02, 0x19, "partly clear"],
    3: [0x03, 0x19, "overcast"],
    45: [0x83, 0x83, "fog"],
    48: [0x44, 0x44, "depositing rime fog"],
    51: [0x47, 0x5A, "light drizzle"],
    53: [0x48, 0x5B, "moderate drizzle"],
    55: [0x49, 0x5C, "dense drizzle"],
    56: [0x07, 0x1A, "light freezing drizzle"],
    57: [0x08, 0x1B, "dense freezing drizzle"],
    61: [0x04, 0x1A, "slight rain"],
    63: [0x05, 0x1B, "moderate rain"],
    65: [0x06, 0x1C, "heavy rain"],
    66: [0x04, 0x1A, "light freezing rain"],
    67: [0x45, 0x1C, "heavy freezing rain"],
    71: [0x10, 0x20, "slight snowfall"],
    73: [0x10, 0x20, "moderate snowfall"],
    75: [0x11, 0x21, "heavy snowfall"],
    77: [0x10, 0x20, "snow grains"],
    80: [0x07, 0x1A, "slight rain showers"],
    81: [0x08, 0x1B, "moderate rain showers"],
    82: [0x09, 0x1C, "heavy rain showers"],
    85: [0x12, 0x20, "slight snow showers"],
    86: [0x13, 0x21, "heavy snow showers"],
    95: [0x0A, 0x1D, "slight or moderate thunderstorm"],
    96: [0x0B, 0x1E, "slight hail thunderstorm"],
    99: [0x4C, 0x4C, "heavy hail thunderstorm"],
    255: [0x17, 0x23, "unknown"],
}


def om_get_pictogram_index_from_code(wmo_code: int, is_day: bool) -> int:
    p = WMO_CODE_LOOKUP.get(wmo_code, [0x16, 0x22, "unkown"]);
    if is_day == True:
        return p[0]
    else:
        return p[1]


def om_get_label_from_code(wmo_code: int):
    p = WMO_CODE_LOOKUP.get(wmo_code, [0x16, 0x22, "unkown"]);
    return p[2]


def om_get_encoded_rain_proba(proba):
    thresholds = [2.5, 7.5, 15, 22.5, 27.5, 35, 45, 55, 65, 72.5, 77.5, 85, 92.5, 97];
    for index, threshold in enumerate(thresholds):
        if proba < threshold:
            return index
    return 0xe;

# get from open-meteo.com
def get_openmeteo(v, location, latlong):
    if (latlong == location == None):
        error("You must provide a --location or a --latlong")
        quit(-3)
    if (latlong == None):
        debug(v, f"Geocoding location : {location} ...")
        geocode = om_geocode_city(location)
        debug(v, f"Found location : {geocode}")
        lat, lon, tz, place_name = geocode
    else:
        lat, lon = map(float, latlong.split(","))
        tz = "auto"
        place_name = "?"

    debug(v, "Fetching forecast...")
    data = om_fetch_5day(lat, lon, tz)

    # Find temp min and max for today and 5 next days
    if (len(data["hourly"]['time']) != 24):
        error("ERROR : not receiving 24 forecast")
        quit(-1)
    forecast = [{} for _ in range(0, 6)]
    for days in range(0, 6):  # today + 5 days forcast
        tmin = 99
        tmax = -99
        wco_day = -1
        rain = 0
        wco_q0 = data["hourly"]["weather_code"][(days * 4)] #earl
        wco_q1 = data["hourly"]["weather_code"][(days * 4) + 1]
        wco_q2 = data["hourly"]["weather_code"][(days * 4) + 2]
        wco_q3 = data["hourly"]["weather_code"][(days * 4) + 3]
        for quarterday in range(0, 4):  # 4 times a day
            #night is q0 (03:00)
            #matinee is q1 09:00
            #afternoon is q2 15:00
            #evening is q3 21:00
            # day is matinee+afternoon+evening
            i = (days * 4) + quarterday
            # temperature
            t = data["hourly"]["temperature_2m_min"][i]
            if t < tmin:
                tmin = t
            t = data["hourly"]["temperature_2m_max"][i]
            if t > tmax:
                tmax = t
                # weather code (used for picto)
            wco = data["hourly"]["weather_code"][i]
            if (quarterday == 0):
                wco_night = wco  # take the first quarterday (03:00) for the night
            else:
                if (wco > wco_day):
                    wco_day = wco  # for day, take the best of the 3 other quarter
                    # rain proba
            t = data["hourly"]["precipitation_probability"][i]
            if (t > rain):
                rain = t
            
        forecast[days]['date'] = data["hourly"]["time"][i][:10]       
        forecast[days]['tmin'] = math.floor(tmin)
        forecast[days]['tmax'] = math.ceil(tmax)
        w = {
            'weather_code': wco_day,
            'picto': om_get_pictogram_index_from_code(wco_day, True),
            'label': om_get_label_from_code(wco_day)
        }
        forecast[days]['weathercode_day'] = w
        w = {
            'weather_code': wco_night,
            'picto': om_get_pictogram_index_from_code(wco_night, False),
            'label': om_get_label_from_code(wco_night)
        }
        forecast[days]['weathercode_night'] = w
        forecast[days]['rain'] = rain
        forecast[days]['rain_encoded'] = om_get_encoded_rain_proba(rain)
        forecast[days]['weathercode_q0'] = {
            'weather_code': wco_q0,
            'picto': om_get_pictogram_index_from_code(wco_q0, False),
            'label': om_get_label_from_code(wco_q0)
        }
        forecast[days]['weathercode_q1'] = {
            'weather_code': wco_q1,
            'picto': om_get_pictogram_index_from_code(wco_q1, True),
            'label': om_get_label_from_code(wco_q1)
        }
        forecast[days]['weathercode_q2'] = {
            'weather_code': wco_q2,
            'picto': om_get_pictogram_index_from_code(wco_q2, True),
            'label': om_get_label_from_code(wco_q2)
        }
        forecast[days]['weathercode_q3'] = {
            'weather_code': wco_q3,
            'picto': om_get_pictogram_index_from_code(wco_q3, False),
            'label': om_get_label_from_code(wco_q3)
        }
        
    return forecast


def main():
    global VERBOSE
    parser = argparse.ArgumentParser(description="This tool generate a StarMeteo compatible message for weather forcast.")
    parser.add_argument("--verbose", action="store_true",
        help="Enable debug output")

    parser.add_argument("--backend", "-b",
        help="Indicates which weather forecast backend to use. Can be \"openmeteo\", \"weatherunderground\", or \"none\" or \"file\" followed by a file path.",
        #choices=["weatherunderground", "wu", "openmeteo", "om", "file", "none"],
        nargs="+", # one or two value (for file backend)
        metavar=("BACKEND", "FILE"),
        default="none"
    )
    parser.add_argument("--days", "-d", type=int,
        help="Number of forcast days. Default is 6",
        default="6"
    )
    parser.add_argument("--location", "-l",
        help="Indicates the location to get weather for (eg : \"Paris, France\")",
        default=None
    )
    parser.add_argument("--latlong", "-ll",
        help="Indicates latitude longitude, format nnn.nnnn,nnn.nnnn",
        default=None
    )
    parser.add_argument("--output", "-o",
        help="Output format. Default \"starmeteo\"",
        choices=["starmeteo", "json", "txt", "csv"],
        default="starmeteo"
    )

    parser.add_argument("--wu-api",
        dest="wu_api", required=False, type=str,
        help="Weather Underground API key (required when --backend=weatherunderground). Get one from https://www.wunderground.com/member/api-keys")

    args = parser.parse_args()
    VERBOSE = args.verbose
    filename = None
    if args.backend[0] == "file": # the file backned has an extra argument, the path to the file
        if len(args.backend) != 2:
            parser.error("the file backend requires a file path")
        filename = args.backend[1]
        args.backend = args.backend[0]
    elif len(args.backend) != 1:
        parser.error("a file path is only valid with the file backend")
    elif args.backend[0] not in {
        "weatherunderground",
        "wu",
        "openmeteo",
        "om",
        "none",
    }:
        parser.error(f"invalid backend: {args.backend[0]}")   
    else:
        args.backend = args.backend[0]
    if args.backend == "wu":
        args.backend = "weatherunderground"
    if args.backend == "om":
        args.backend = "openmeteo"
    if args.backend == "weatherunderground":
        if not args.wu_api:
            error('Missing --wu-api. It is required when --backend="weatherunderground".')
            return (-1)
        debug(args.verbose, "Using Weather Underground backend.")
    if args.backend == "openmeteo":
        forecast = get_openmeteo(args.verbose, args.location, args.latlong)
    elif args.backend == "weatherunderground":
        forecast = get_weatherunderground(args.verbose, args.location, args.latlong, args.wu_api)
    elif args.backend == "none":
        forecast = get_local_forecast(args.verbose, args)
    elif args.backend == "file":
        debug(VERBOSE, f"Get info from file {filename}")
        with open(filename, "r", encoding="utf-8") as file:
            forecast = json.load(file)
    else:
        error("Wrong backend")
        return (2)
    
    forecast = forecast[:args.days] # keep only days requested
    debug(VERBOSE, "Forecast :")
    debug(VERBOSE, forecast)
    if (args.output == "json"):
        print(json.dumps(forecast, indent=4))
    elif (args.output == "txt"):
        print("== FORECAST ==")
        for i in forecast:
            print('== ',i['date'])
            print(f"    T min : {i['tmin']:+03d} | T max : {i['tmax']:+03d}")
            print(f"    Day   : {i['weathercode_day']['label']:<16} | Night : {i['weathercode_night']['label']:<16}   | Rain : {i['rain']}")
            print(f"    Night : {i['weathercode_q0']['label']:<16} | Morning : {i['weathercode_q1']['label']:<16} | Afternoon : {i['weathercode_q2']['label']:<16} | Evening : {i['weathercode_q3']['label']:<16} " )
    elif (args.output == "csv"):
        print("date;tmin;tmax;weather_code_day;picto_day;label_day;weather_code_night;picto_night;label_night;rain")
        for i in forecast:
            print(f"{i['date']};{i['tmin']};{i['tmax']};{i['weathercode_day']['weather_code']};{i['weathercode_day']['picto']};{i['weathercode_day']['label']};{i['weathercode_night']['weather_code']};{i['weathercode_night']['picto']};{i['weathercode_night']['label']};{i['rain']};")
    elif (args.output == "starmeteo"):
        # printf("%s -forecast:[LowTemp],[HighTemp],[MainPicto_Hex],[Picto_2_Hex],[Picto_3_Hex],[Picto_4_Hex],[Picto_5_Hex]\n",argv[0]);
        smout = ""
        for i in forecast:
            smout = smout + (
                f"-forecast:{i['tmin']},{i['tmax']},"
                f"{i['weathercode_day']['picto']:#x},"
                f"{i['weathercode_q0']['picto']:#x},{i['weathercode_q1']['picto']:#x},"
                f"{i['weathercode_q2']['picto']:#x},{i['weathercode_q3']['picto']:#x}"
             ) + " "
        print(smout)
if __name__ == "__main__":
    main()
'''
0x01 : nuage clair et soleil clar
0x4c : gros nuage de pluie
./starmeteo -forecast:-10,40,0x4c,0x1,0x1,0x1,0x1 
                       1  2  3    5   5   6   7
  1 temp min
  2 temp max
  3 "fixe" journee entiere
  4 nuit
  5 matinee
  6 : apres midi
  7 : soiree
'''
