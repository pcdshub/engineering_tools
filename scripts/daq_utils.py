####################################################
# Utilities to run the daq and view its status.
#
# Do not use non-standard python.
####################################################
import getpass
import os
import subprocess
import time
from subprocess import PIPE

DAQMGR_HUTCHES = ["tmo", "rix", "txi", "xpp", "mfx", "ued"]
MAX_RETRIES = 10
# The daq and analysis setup scripts refuse to load over each other, so each
# daqmgr call has to source the one matching its cnf.
ENV_DAQ = "setup_env_daq.sh"
ENV_ANA = "setup_env_ana.sh"


def call_subprocess(*args):
    return str(subprocess.check_output(args, stderr=PIPE).strip(), "utf-8")


class SbatchManager:
    def __init__(self, user):
        self.user = user

    def get_job_info(self):
        # Use squeue to get JobId, Comment, JobName, Status, and Reasons (Node List)
        format_string = '"%i %k %j %T %R"'
        lines = call_subprocess(
            "squeue", "-u", self.user, "-h", "-o", format_string
        ).splitlines()
        job_details = {}
        for i, job_info in enumerate(lines):
            cols = job_info.strip('"').split()
            success = True
            if len(cols) == 5:
                job_id, comment, job_name, state, nodelist = cols
            elif len(cols) > 5:
                job_id, comment, job_name, state = cols[:4]
                nodelist = " ".join(cols[5:])
            else:
                success = False
            if success:
                # Get logfile from job_id
                scontrol_lines = call_subprocess(
                    "scontrol", "show", "job", job_id
                ).splitlines()
                logfile = ""
                for scontrol_line in scontrol_lines:
                    if scontrol_line.find("StdOut") > -1:
                        scontrol_cols = scontrol_line.split("=")
                        logfile = scontrol_cols[1]

                job_details[job_name] = {
                    "job_id": job_id,
                    "comment": comment,
                    "state": state,
                    "nodelist": nodelist,
                    "logfile": logfile,
                }
        return job_details


class DaqManager:
    def __init__(self, verbose=False, daq=False, ami=False, daq_cnf=None, ami_cnf=None):
        """Manage the daq for the hutch this machine belongs to.

        The daq is two halves with separate conda environments: the daq
        proper, from <hutch>_daq.py with setup_env_daq.sh, and ami, from
        <hutch>_ami.py with setup_env_ana.sh. Both live in the operator's
        daq/scripts directory.

        daq, ami: which component to act on. Naming neither acts on both, which
            is what an operator running restartdaq with no arguments expects as the
            default behavior.
        daq_cnf, ami_cnf: replace a component's default cnf file. Relative to the 
            operator's daq/scripts directory.
        """
        self.verbose = verbose
        self.hutch = call_subprocess("get_info", "--gethutch")
        if len(self.hutch) != 3:
            raise ValueError(f"Invalid hutch name found (hutch: '{self.hutch}')")

        self.user = self.hutch + "opr"
        self.sbman = SbatchManager(self.user)
        self.scripts_dir = f"/sdf/home/{self.hutch[0]}/{self.hutch}opr/daq/scripts"
        # Naming neither component means both.
        self.daq = daq or not ami
        self.ami = ami or not daq
        self.daq_cnf = daq_cnf or f"{self.hutch}_daq.py"
        self.ami_cnf = ami_cnf or f"{self.hutch}_ami.py"

    def vprint(self, msg):
        if self.verbose:
            print(msg)

    def release_of(self, path):
        """The release a setup script symlink resolves to.

        Worth reporting: the setup_env_*.sh links are maintained by hand, so
        the one named for a component is not necessarily the release the hutch
        is actually using.
        """
        return os.path.basename(os.path.dirname(os.path.realpath(path)))

    def isdaqmgr(self, quiet=False):
        if self.hutch in DAQMGR_HUTCHES:
            if not quiet:
                print("true")
            return True
        else:
            if not quiet:
                print("false")
            return False

    def isvaliduser(self):
        return getpass.getuser() == self.user

    def waitfor(self, subcmd):
        if subcmd == "stop":
            daq_host = self.wheredaq(quiet=True)
            if daq_host is not None:
                if self.isdaqmgr(quiet=True):
                    for i_retry in range(MAX_RETRIES):
                        daq_host = self.wheredaq(quiet=True)
                        if daq_host is None:
                            break
                        print(f"wait for the DAQ to stop #retry: {i_retry}")
                        time.sleep(1)
                else:
                    print(
                        f"The DAQ did not stop properly (DAQ HOST: {daq_host}), exit now and try again or call your POC or the DAQ phone"
                    )

    def wheredaq(self, quiet=False):
        """Locate where the daq is running.

        We use slurm to check if the hutch user is running control_gui.
        """
        daq_host = None
        # Use control_gui job name to locate the running host for the daq
        job_details = self.sbman.get_job_info()
        if "control_gui" in job_details:
            daq_host = job_details["control_gui"]["nodelist"]

        if not quiet:
            if daq_host is None:
                print(f"DAQ is not running in {self.hutch}")
            else:
                print(f"DAQ is running on {daq_host}")
        return daq_host

    def calldaq(self, subcmd, cnf_file, env_script, wait=True):
        """Run daqmgr here, in the environment that goes with this cnf.

        daqmgr always runs on the machine the command was typed on. The cnf
        says where the daq processes go; the only thing daqmgr's own host
        decides is where the cnf entries without a host of their own land
        (daqstat, control_gui, ami-client), and those are monitors that render
        to $DISPLAY anyway.
        """
        setup = os.path.join(self.scripts_dir, env_script)
        cnf_path = os.path.join(self.scripts_dir, cnf_file)
        # Checked rather than chained with ';': if the setup script refuses to
        # load, daqmgr must not run from whatever is already on PATH.
        cmd = f"cd {self.scripts_dir} || exit 1; "
        cmd += f"source {setup} || exit 1; "
        cmd += f"daqmgr {subcmd} {cnf_path}"

        self.vprint(f"  loading env {env_script} ({self.release_of(setup)})")
        self.vprint(f"  daqmgr {subcmd} {cnf_file}")

        # bash, not sh: the setup scripts use [[ ]] and return.
        ret = subprocess.run(["bash", "-c", cmd])
        self.vprint(f"  daqmgr {subcmd} exited {ret.returncode}")

        if wait:
            # waitfor reports its own retries, and only acts on a stop.
            self.waitfor(subcmd)

    def stopdaq(self):
        """Stop the running daq for the current user.
        Note that daq host is determined by querying slurm job status.
        """
        if self.ami:
            self.calldaq("stop", self.ami_cnf, ENV_ANA, wait=False)
        if self.daq:
            self.calldaq("stop", self.daq_cnf, ENV_DAQ)

    def restartdaq(self):
        # A restart sources both setup scripts, and each refuses to load over
        # the other. Caught up front because of the asymmetry: a leaked
        # ENV_TYPE=ana lets the ami stop succeed and then fails the daq
        # restart, leaving ami stopped and the daq untouched.
        self.vprint(f"hutch {self.hutch}, expecting account {self.user}")
        self.vprint(f"scripts dir {self.scripts_dir}")

        env_type = os.environ.get("ENV_TYPE")
        self.vprint(f"checking shell env: ENV_TYPE={env_type or '(unset)'}")
        if env_type:
            kind = "An analysis" if env_type == "ana" else "A DAQ"
            print(
                f"{kind} env is already loaded in this shell, "
                "please run from a fresh terminal"
            )
            return

        if not self.isvaliduser():
            print("Please run the DAQ from the operator account!")
            return
        self.vprint(f"running as {getpass.getuser()}, ok")

        self.wheredaq()
        st = time.monotonic()
        if self.daq and self.ami:
            # ami-meb lives in the daq cnf and writes the shmem segment the
            # ami nodes read, so the readers stop before the writer is
            # replaced and start again after it.
            print("Restarting both DAQ and AMI.")
            self.calldaq("stop", self.ami_cnf, ENV_ANA, wait=False)
            self.calldaq("restart", self.daq_cnf, ENV_DAQ)
            self.calldaq("start", self.ami_cnf, ENV_ANA, wait=False)
        elif self.daq:
            print("Restarting DAQ only.")
            self.calldaq("restart", self.daq_cnf, ENV_DAQ)
        elif self.ami:
            print("Restarting AMI only.")
            self.calldaq("restart", self.ami_cnf, ENV_ANA, wait=False)
        en = time.monotonic()
        print(f"took {en-st:.4f}s. for starting the DAQ")  # noqa: E231
