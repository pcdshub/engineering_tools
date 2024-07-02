#!/usr/bin/env python
"""
Pretty prints archiver details of a PV.
"""

import argparse
import json

import requests


def main():
    parser = argparse.ArgumentParser(
        prog='archive-details', description=__doc__
    )

    parser.add_argument("pv")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Print _all_ fields available")
    parser.add_argument("-j", "--json", action="store_true",
                        help="Return data, rather than pretty print, to stdout for further processing")

    args = parser.parse_args()

    include_fields = [
        'PV Name',
        'Channel Name',
        'Is this PV currently connected?',
        'When did we receive the last event?',
        'Is this PV paused:',
        'Instance archiving PV',
        'Number of elements:',
        'Precision',
        'Units',
        'Sampling method:',
        'Sampling period:',
        'Are we using PVACCESS?',
        'Extra info - MDEL:',
        'Extra info - ADEL:',
        'Extra info - SCAN:',
        'Extra info - RTYP:',
        'Host name'
    ]

    pv = args.pv
    request_str = "http://pscaa01.slac.stanford.edu:17665/mgmt/bpl/getPVDetails?pv={}".format(pv)
    resp = requests.get(request_str)
    if args.json:
        # Had to use .text and json library rather than .json() to get
        # external apps like jq to take the output here.
        parsed = json.loads(resp.text)
        print(json.dumps(parsed))
    else:
        if args.debug:
            print("\n")
            for d in resp.json():
                print("\t{} : {}".format(d['name'], d['value']))
            print("\n")

        else:
            print("\n")
            for field in include_fields:
                for entry in resp.json():
                    if entry['name'] == field:
                        print("\t{} : {}".format(entry['name'], entry['value']))
            print("\n")


if __name__ == '__main__':
    main()
