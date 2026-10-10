#!/usr/bin/env python3
"""Encode or decode StarMeteo frames."""

import argparse
import sys
import re
from datetime import datetime
import sm_time
import sm_forecast

from sm_utils import debug, decode
import sm_utils




_USE_CURRENT_TIME = object()


KNOWN_OPTIONS = {
    "-h", "--help",
    "-d", "--decode",
    "-f", "--fast",
    "-t", "--time",
    "-fc", "--forecast",
    "-a", "--area",
    "-i", "--interval",
    "--verbose",
    "-n",
}


def normalize_forecast_args(argv):
    """Accept forecast values that begin with '-' without treating them as flags."""
    normalized = []
    i = 0
    while i < len(argv):
        token = argv[i]
        if token in {"-fc", "--forecast"} and i + 1 < len(argv):
            next_token = argv[i + 1]
            if next_token.startswith("-") and next_token not in KNOWN_OPTIONS:
                normalized.append(f"{token}={next_token}")
                i += 2
                continue
        normalized.append(token)
        i += 1
    return normalized


def parse_datetime(value):
    for date_format in ("%Y-%m-%d:%H:%M", 
                        "%Y-%m-%d:%H:%M:%S", 
                        "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(value, date_format)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(
        "datetime must use YYYY-MM-DD:hh:mm or YYYY-MM-DD:hh:mm:ss format"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Encode or decode StarMeteo frames."
    )
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument(
        "-d",
        "--decode",
        nargs="?",  
        const="",
        metavar="DATA",
        help="Decode frame data from DATA or stdin.",
    )
    parser.add_argument(
            "-f",
            "--fast",
            action="store_true",
            help="Faster way to decode (to be used with -d/--decode)",
        )
    operation.add_argument(
        "-t",
        "--time",
        nargs="?",
        const=_USE_CURRENT_TIME,
        type=parse_datetime,
        metavar="DATETIME",
        help="Date-time in YYYY-MM-DD:hh:mm format (defaults to now).",
    )
    operation.add_argument(
        "-fc",
        "--forecast",
        action="append",
        nargs="+",
        metavar="STRING",
        help="Forecast value(s) : Tmin,Tmax,FullDayIcon,NightIcon,MorningIcon,AfternoonIcon,EveningIcon[,Rain] . Rain is optional, value from 0 to 100. Use --area to change default area.",
    )
    parser.add_argument(
        "-a",
        "--area",
        metavar="AREAS",
        default="75",
        help="Comma-separated list of areas (for example: 75,92,95; default: 75).",
    )
    parser.add_argument(
        "-i",
        "--interval",
        metavar="INTERVAL", 
        default="12", type=int,
        help="Interval in minutes (default: 12) for the weatherstation to wait for forecast.",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug output.")
    parser.add_argument("-n", action="store_true", help="Do not output the trailing newline.")
    args = parser.parse_args(normalize_forecast_args(sys.argv[1:]))
    
    if args.forecast is not None:
        args.forecast = [value for group in args.forecast for value in group]
    
    if args.decode is not None:
        data = args.decode if args.decode else sys.stdin.read()
        debug(args.verbose, f"Decoding data: <<{data}>>")
        sm_utils.decode(
            args.verbose,
            data,
            args.fast
        )
        pass
    if (args.time is not None):
        date_time = (
            datetime.now() if args.time is _USE_CURRENT_TIME else args.time
        )
        # split area by space or ,
        areas = [int(a, 0) for a in re.split(r'[\s,]+', args.area) if a]
        encoded_data = sm_time.sm_encode_datetime(
                date_time, 
                areas, 
                args.interval,
                args.verbose)
        debug(args.verbose, f"<<Encoded data>>: <<{encoded_data}>>")
        print(encoded_data, end="" if args.n else "\n")
    if (args.forecast is not None):
        args.area = int(args.area, 0)
        encoded_data = sm_forecast.sm_encode_forecast(
                args.forecast,
                args.area,
                args.verbose)
        debug(args.verbose, f"<<Encoded forecast data>>: <<{encoded_data}>>")
        print(encoded_data, end="" if args.n else "\n")


if __name__ == "__main__":
    main()