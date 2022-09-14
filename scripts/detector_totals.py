#!/usr/bin/env python
"""
Script for the detector group to pull totals out of the elog.
We get DAQ run parameters for all experiments and count them up.
"""
import os
import json
import logging
import argparse
import requests
from datetime import datetime
from collections import OrderedDict
from krtc import KerberosTicket


logger = logging.getLogger(__name__)

krbheaders = KerberosTicket("HTTP@pswww.slac.stanford.edu").getAuthHeaders()

def getDAQDetectorTotals(experiment):
    """Returns a total number of events per detector for this experiment"""
    logger.info(f"Getting DAQ Detector totals for {experiment}")
    ret = OrderedDict()

    resp = requests.get(f"https://pswww.slac.stanford.edu/ws-kerb/lgbk//lgbk/{experiment}/ws/run_table_sources", headers=krbheaders).json()
    rps = resp["value"].get("DAQ", [])
    daqdets = map(lambda x: x["source"].replace("params.", ""), filter(lambda x: x["label"].startswith("DAQ Detectors/"), rps))
    rpvals = requests.get(f"https://pswww.slac.stanford.edu/ws-kerb/lgbk//lgbk/{experiment}/ws/get_run_params_for_all_runs",
        params={"param_names": ",".join(list(daqdets) + [ "DAQ Detector Totals/Events" ])}, headers=krbheaders).json()["value"]
    for run in rpvals:
        eventcount = run["params"].get("DAQ Detector Totals/Events", None)
        dets_in_run = filter(lambda x: x.startswith("DAQ Detectors/"), run["params"].keys())
        if eventcount and dets_in_run:
            for detector in dets_in_run:
                if detector not in ret:
                    ret[detector] = 0
                ret[detector] = ret[detector] + int(eventcount)
    return ret


def getExperiments(run_period):
    """ Return all the experiments that end with the run period; for example, all experiments that end with 18 for run period 18"""
    resp = requests.get("https://pswww.slac.stanford.edu/ws-kerb/lgbk/lgbk/ws/experiments", params={"categorize": "instrument_runperiod", "sortby" : "name"}, headers=krbheaders).json()
    exps = []
    for k,v in resp["value"].items():
        insexps = map(lambda x: x["_id"], v.get("Run " + str(run_period), []))
        exps.extend(insexps)
    return exps

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose",    action='store_true', help="Turn on verbose logging")
    parser.add_argument("--run_period", action='store', help="The last two digits of the run period, for example 18", default="18")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    experiments = getExperiments(args.run_period)
    logger.debug(experiments)
    daq_counts = OrderedDict()
    for experiment in experiments:
        logger.debug("Getting DAQ detector counts for %s", experiment)
        daq_counts[experiment] = getDAQDetectorTotals(experiment)

    det_counts = OrderedDict()
    for experiment, detectors in daq_counts.items():
        print("DAQ totals for experiment {0}".format(experiment))
        for detector, count in detectors.items():
            print("{0: <32} --> {1}".format(detector, count))
            if detector not in det_counts:
                det_counts[detector] = 0
            det_counts[detector] = det_counts[detector] + count

    print("Totals across all experiments")
    for detector, count in det_counts.items():
        print("{0: <32} --> {1}".format(detector.replace("DAQ Detectors/", ""), count))
