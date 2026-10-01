#!/usr/bin/env python3
"""Encode or decode StarMeteo frames."""

import argparse
import sys
from datetime import datetime
import sm_time


_USE_CURRENT_TIME = object()


def parse_datetime(value):
    for date_format in ("%Y-%m-%d:%H:%M", "%Y-%m-%d:%H:%M:%S"):
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
        "--area",
        metavar="AREAS",
        default="75",
        help="Comma-separated list of areas (for example: 75,92,95; default: 75).",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug output.")
    parser.add_argument("-n", action="store_true", help="Do not output the trailing newline.")
    args = parser.parse_args()

    
    if args.decode is not None:
        data = args.decode if args.decode else sys.stdin.read()
        # TODO: Implement frame decoding.
        pass
    else:
        date_time = (
            datetime.now() if args.time is _USE_CURRENT_TIME else args.time
        )
        areas = [area.strip() for area in args.area.split(",")]
        print(
            sm_time.sm_encode_datetime(date_time, areas, args.verbose),
            end="" if args.n else "\n"
        )


if __name__ == "__main__":
    main()