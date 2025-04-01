####################################################
# Utilities to run the daq and view its status.
#
# Do not use non-standard python.
####################################################
import getpass
import logging
import os
import socket
import subprocess
import sys
import time
from subprocess import PIPE

DAQMGR_HUTCHES = ["tmo", "rix", "txi", "mfx"]
LOCALHOST = socket.gethostname()
SLURM_PARTITION = "drpq"
SLURM_JOBNAME = "submit_daq"
SLURM_OUTPUT = "slurm_daq.log"
MAX_RETRIES = 10


def call_subprocess(*args):
    try:
        output = subprocess.check_output(args, stderr=PIPE).strip()
        return output.decode("utf-8")
    except subprocess.CalledProcessError as e:
        logging.error("Subprocess call '%s' failed with error: %s", " ".join(args), e)
        raise


def call_sbatch(cmd, nodelist, scripts_dir):
    sb_script = "#!/bin/bash\n"
    sb_script += f"#SBATCH --partition={SLURM_PARTITION}\n"
    sb_script += f"#SBATCH --job-name={SLURM_JOBNAME}\n"
    sb_script += f"#SBATCH --nodelist={nodelist}\n"
    sb_script += f"#SBATCH --output={os.path.join(scripts_dir, SLURM_OUTPUT)}\n"
    sb_script += "#SBATCH --ntasks=1\n"
    sb_script += "unset PYTHONPATH\n"
    sb_script += "unset LD_LIBRARY_PATH\n"
    sb_script += cmd

    try:
        result = subprocess.run(
            ["sbatch", "-"],
            input=sb_script,
            text=True,
            stdout=PIPE,
            stderr=PIPE,
            check=True,
        )
        logging.debug("sbatch submission result: %s", result.stdout.strip())
    except subprocess.CalledProcessError as e:
        logging.error("sbatch submission failed: %s", e.stderr.strip())
        raise


class SbatchManager:
    def __init__(self, user):
        self.user = user

    def get_job_info(self):
        format_string = '"%i %k %j %T %R"'
        try:
            output = call_subprocess(
                "squeue", "-u", self.user, "-h", "-o", format_string
            )
            lines = output.splitlines()
        except Exception as e:
            logging.error("Failed to get job info from squeue: %s", e)
            return {}

        job_details = {}
        for job_info in lines:
            cols = job_info.strip('"').split()
            if len(cols) >= 5:
                job_id, comment, job_name, state = cols[:4]
                nodelist = " ".join(cols[4:])
            else:
                logging.warning("Unexpected job info format: %s", job_info)
                continue

            try:
                scontrol_output = call_subprocess("scontrol", "show", "job", job_id)
                logfile = ""
                for scontrol_line in scontrol_output.splitlines():
                    if "StdOut" in scontrol_line:
                        parts = scontrol_line.split("=")
                        if len(parts) > 1:
                            logfile = parts[1]
            except Exception as e:
                logging.error("Failed to get scontrol info for job %s: %s", job_id, e)
                logfile = ""

            job_details[job_name] = {
                "job_id": job_id,
                "comment": comment,
                "state": state,
                "nodelist": nodelist,
                "logfile": logfile,
            }
        return job_details


class DaqManager:
    def __init__(self, verbose=False, cnf=None):
        self.verbose = verbose
        try:
            self.hutch = call_subprocess("get_info", "--gethutch")
        except Exception as e:
            logging.error("Failed to get hutch info: %s", e)
            raise
        if len(self.hutch) != 3:
            raise ValueError(f"Invalid hutch name found (hutch: '{self.hutch}')")

        self.user = self.hutch + "opr"
        self.sbman = SbatchManager(self.user)
        self.scripts_dir = f"/reg/g/pcds/dist/pds/{self.hutch}/scripts"
        self.cnf_file = f"{self.hutch}.py" if cnf is None else cnf
        logging.debug(
            "DaqManager initialized for hutch %s with config %s",
            self.hutch,
            self.cnf_file,
        )

    def isdaqmgr(self):
        result = self.hutch in DAQMGR_HUTCHES
        msg = "true" if result else "false"
        logging.debug("isdaqmgr: %s", msg)
        if result:
            sys.exit(0)
        else:
            sys.exit(1)

    def isvaliduser(self):
        valid = getpass.getuser() == self.user
        if not valid:
            logging.error(
                "Invalid user. Expected %s but got %s", self.user, getpass.getuser()
            )
        return valid

    def waitfor(self, subcmd):
        if subcmd == "stop":
            daq_host = self.wheredaq_internal()
            if daq_host is not None:
                if self.hutch in DAQMGR_HUTCHES:
                    for i_retry in range(MAX_RETRIES):
                        daq_host = self.wheredaq_internal()
                        if daq_host is None:
                            logging.debug("DAQ has stopped after %d retries.", i_retry)
                            break
                        logging.debug("Waiting for the DAQ to stop, retry #%d", i_retry)
                        time.sleep(1)
                    else:
                        logging.error(
                            "DAQ did not stop after %d retries. Please try again or contact support.",
                            MAX_RETRIES,
                        )
                else:
                    logging.error(
                        "The DAQ did not stop properly (DAQ HOST: %s).", daq_host
                    )

    def wheredaq_internal(self):
        job_details = self.sbman.get_job_info()
        daq_host = None
        if "control_gui" in job_details:
            daq_host = job_details["control_gui"]["nodelist"]
        return daq_host

    def wheredaq(self):
        daq_host = self.wheredaq_internal()
        if daq_host is None:
            msg = f"DAQ is not running in {self.hutch}"
        else:
            msg = f"DAQ is running on {daq_host}"
        logging.debug("wheredaq: %s", msg)
        print(msg)
        return daq_host

    def calldaq(self, subcmd, daq_host=None):
        prog = "daqmgr"
        cmd = f"pushd {self.scripts_dir} > /dev/null; "
        cmd += f'source {os.path.join(self.scripts_dir, "setup_env.sh")}; '
        cmd += f"WHEREPROG=$(which {prog}); set -x; "
        cmd += f"$WHEREPROG {subcmd} {os.path.join(self.scripts_dir, self.cnf_file)}; {{ set +x; }} 2>/dev/null; "
        cmd += "popd > /dev/null;"

        if subcmd == "restart":
            query_daq_host = self.wheredaq()
        else:
            query_daq_host = self.wheredaq_internal()

        if daq_host is None:
            daq_host = query_daq_host
            if daq_host is None:
                daq_host = LOCALHOST

        logging.debug("Executing command on host: %s", daq_host)
        if daq_host == LOCALHOST:
            try:
                ret = subprocess.run(
                    cmd, stdout=PIPE, stderr=PIPE, shell=True, check=True
                )
                logging.debug("Command output: %s", ret.stdout.decode())
            except subprocess.CalledProcessError as e:
                logging.error("Local command failed: %s", e.stderr.decode())
        else:
            try:
                call_sbatch(cmd, daq_host, self.scripts_dir)
            except Exception as e:
                logging.error("Failed to submit sbatch command: %s", e)

        self.waitfor(subcmd)

    def stopdaq(self):
        print("Stopping DAQ...")
        self.calldaq("stop")

    def restartdaq(self, daq_host):
        if not self.isvaliduser():
            logging.error("Please run the DAQ from the operator account!")
            return
        st = time.monotonic()
        self.calldaq("restart", daq_host=daq_host)
        en = time.monotonic()
        print("Restarted DAQ in %.4f seconds.", en - st)
