#!/usr/bin/env python3
"""Encode or decode StarMeteo frames."""

import argparse
import sys
from datetime import datetime
import sm_time
import re

from sm_utils import debug, decode
import sm_utils


_USE_CURRENT_TIME = object()


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
    operation.add_argument(
        "-t",
        "--time",
        nargs="?",
        const=_USE_CURRENT_TIME,
        type=parse_datetime,
        metavar="DATETIME",
        help="Date-time in YYYY-MM-DD:hh:mm format (defaults to now).",
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
    args = parser.parse_args()

    if args.decode is not None:
        data = args.decode if args.decode else sys.stdin.read()
        debug(args.verbose, f"Decoding data: <<{data}>>")
        sm_utils.decode(
            args.verbose,
            data
        )
        pass
    else:
        date_time = (
            datetime.now() if args.time is _USE_CURRENT_TIME else args.time
        )
        # split area by space or ,
        areas = [int(a) for a in re.split(r'[\s,]+', args.area) if a]
        encoded_data = sm_time.sm_encode_datetime(
                date_time, 
                areas, 
                args.interval,
                args.verbose)
        
        
        debug(args.verbose, f"<<Encoded data>>: <<{encoded_data}>>")
        print(encoded_data, end="" if args.n else "\n")
        


if __name__ == "__main__":
    main()