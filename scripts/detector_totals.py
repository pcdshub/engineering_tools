#!/usr/bin/env python
"""
Script for the detector group to pull totals out of the elog.
We get DAQ run parameters for all experiments and count them up.
"""
import argparse
import logging
import sys
from collections import OrderedDict

import dateutil.parser as dateparser
import pytz
import requests
from krtc import KerberosTicket

logger = logging.getLogger(__name__)
krbheaders = KerberosTicket("HTTP@pswww.slac.stanford.edu").getAuthHeaders()
tz = pytz.timezone('America/Los_Angeles')
lgbkprefix = "https://pswww.slac.stanford.edu/ws-kerb/lgbk/lgbk/"


def getDAQDetectorTotals(experiment):
    """Returns a total number of events per detector for this experiment"""
    logger.info(f"Getting DAQ Detector totals for {experiment}")
    ret = OrderedDict()

    resp = requests.get(
        f"{lgbkprefix}/{experiment}/ws/run_table_sources",
        headers=krbheaders)
    resp.raise_for_status()
    rps = resp.json()["value"].get("DAQ", [])
    daqdets = map(lambda x: x["source"].replace("params.", ""),
                  filter(lambda x: x["label"].startswith("DAQ Detectors/"),
                         rps))
    detevnms = ",".join(list(daqdets) + ["DAQ Detector Totals/Events"])
    rpvals = requests.get(
        f"{lgbkprefix}/{experiment}/ws/get_run_params_for_all_runs",
        params={"param_names": detevnms},
        headers=krbheaders).json()["value"]
    for run in rpvals:
        eventcount = run["params"].get("DAQ Detector Totals/Events", None)
        dets_in_run = filter(lambda x: x.startswith("DAQ Detectors/"),
                             run["params"].keys())
        if eventcount and dets_in_run:
            for detector in dets_in_run:
                if detector not in ret:
                    ret[detector] = 0
                ret[detector] = ret[detector] + int(eventcount)
    return ret


def getExperiments(run_period, after, before):
    """ Return all the experiments in the specified run period.
    Also, if start and end are specified, include other experiments as follows
    after - If not None, also include other experiments
        except those whose last run is before the specified time
    before - If not None, also include other experiments
        except those whose first run is after the specified time
    """
    resp = requests.get(
        f"{lgbkprefix}/ws/experiments",
        params={"categorize": "instrument_runperiod",
                "sortby": "name"},
        headers=krbheaders
    ).json()
    exps = []
    for k, v in resp["value"].items():
        insexps = map(lambda x: x["_id"], v.get("Run " + str(run_period), []))
        exps.extend(insexps)

    def last_run_exists(exp):
        return exp.get("last_run", {}).get("begin_time", None)

    def first_run_exists(exp):
        return exp.get("first_run", {}).get("begin_time", None)

    def last_run_before_specified_after(exp):
        return (exp.get("last_run", {}).get("begin_time", None)
                and dateparser.parse(exp["last_run"]["begin_time"])
                .astimezone(tz) < after)

    def first_run_after_specified_before(exp):
        return (exp.get("first_run", {}).get("begin_time", None)
                and dateparser.parse(exp["first_run"]["begin_time"]).astimezone(tz) > before)

    sef = None
    if after and before:
        def sef(x):
            return (last_run_exists(x)
                    and not last_run_before_specified_after(x)
                    and first_run_exists(x)
                    and not first_run_after_specified_before(x))
    elif after:
        def sef(x):
            return (last_run_exists(x)
                    and not last_run_before_specified_after(x))
    elif before:
        def sef(x):
            return (first_run_exists(x)
                    and not first_run_after_specified_before(x))

    if sef:
        expsset = set(exps)
        for ins, rps in resp["value"].items():
            for rp, el in rps.items():
                for e in el:
                    if sef(e):
                        expsset.add(e["_id"])
        exps = list(expsset)

    return exps


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v",
                        "--verbose",
                        action='store_true',
                        help="Turn on verbose logging")
    parser.add_argument("--run_period",
                        action='store',
                        help="The last two digits of the run period, "
                             "for example 18",
                        required=True,
                        type=int)
    parser.add_argument("--show_matched_experiments_only",
                        action='store_true',
                        help="Only show the matching experiment names;"
                             " do not actually run the report. "
                             "Used for debugging.")
    parser.add_argument("--after",
                        help="Include other experiments except those "
                        "whose last run is before the specified time")
    parser.add_argument("--before",
                        help="Include other experiments except those "
                        "whose first run is after the specified time")

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    def dpp(x):
        dateparser.parse(x).astimezone(tz) if x else None

    after = dpp(args.after)
    before = dpp(args.before)

    experiments = getExperiments(args.run_period, after, before)
    logger.debug(experiments)

    if args.show_matched_experiments_only:
        print("\n".join(sorted(experiments)))
        sys.exit(0)

    daq_counts = OrderedDict()
    for experiment in experiments:
        logger.debug("Getting DAQ detector counts for %s", experiment)
        try:
            daq_counts[experiment] = getDAQDetectorTotals(experiment)
        except:
            logger.exception("Exception getting  DAQ detector counts"
                             " for %s. Note; this may be expected "
                             "( for example, restricted experiments ) ", 
                            experiment)

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
        print("{0: <32} --> {1}"
              .format(detector.replace("DAQ Detectors/", ""), count))
