####################################################
# Utilities to run the daq and view its status.
#
# Do not use non-standard python.
####################################################
import subprocess
from subprocess import PIPE
import socket
import os, sys
import getpass
import time

DAQBATCH_HUTCHES=['tmo', 'rix']
LOCALHOST = socket.gethostname()
SLURM_PARTITION='drpq'
SLURM_JOBNAME='submit_daq'
DAQBATCH_SCRIPT='submit_daq.sh'
DAQBATCH_OUTPUT='slurm_daq.log'
MAX_RETRIES=10

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise

def call_subprocess(*args):
    return subprocess.check_output(args, stderr=PIPE, universal_newlines=True)

def call_sbatch(cmd, nodelist, scripts_dir):
    sb_script = "#!/bin/bash\n"
    sb_script += f"#SBATCH --partition={SLURM_PARTITION}" + "\n"
    sb_script += f"#SBATCH --job-name={SLURM_JOBNAME}" + "\n"
    sb_script += f"#SBATCH --nodelist={nodelist}" + "\n"
    daqbatch_output = os.path.join(scripts_dir, DAQBATCH_OUTPUT)
    sb_script += f"#SBATCH --output={daqbatch_output}" + "\n"
    sb_script += f"#SBATCH --ntasks=1" + "\n"
    sb_script += f"unset PYTHONPATH" + "\n"
    sb_script += f"unset LD_LIBRARY_PATH" + "\n"
    sb_script += cmd
    daqbatch_script = os.path.join(scripts_dir, DAQBATCH_SCRIPT)
    with open(daqbatch_script, "w") as f:
        f.write(sb_script)
    call_subprocess('sbatch', daqbatch_script)
    silentremove(daqbatch_script)

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
    def __init__(self, opts):
        self.opts = opts
        self.verbose = False
        for o, a in self.opts:
            if o in ('-v', '--verbose'):
                self.verbose = True
        self.hutch = call_subprocess("get_info", "--gethutch")
        self.user = self.hutch+'opr'
        self.sbman = SbatchManager(self.user)
        self.scripts_dir = f'/reg/g/pcds/dist/pds/{self.hutch}/scripts'
        self.set_cnf_file_and_platform()

    def isdaqbatch(self, quiet=False):
        if self.hutch in DAQBATCH_HUTCHES:
            if not quiet: print('true')
            return True
        else:
            if not quiet: print('false')
            return False

    def isvaliduser(self):
        if getpass.getuser().find('opr') > -1:
            return True
        return False

    def waitfor(self, subcmd):
        if subcmd == 'stop':
            daq_host = self.wheredaq(quiet=True)
            if daq_host is not None:
                if self.isdaqbatch(quiet=True):
                    for i_retry in range(MAX_RETRIES):
                        daq_host = self.wheredaq(quiet=True)
                        if daq_host is None:
                            break
                        print(f'wait for daqbatch to stop #retry: {i_retry}')
                        time.sleep(1)
                else:
                    print(f'the DAQ did not stop properly (DAQ HOST: {daq_host}), exit now and try again or call your POC or the DAQ phone')

    def set_cnf_file_and_platform(self):
        self.cnf_file = f'{self.hutch}.py'
        
        cc = {'platform': None}
        configfilename = os.path.join(self.scripts_dir, self.cnf_file)
        try:
            exec(compile(open(configfilename).read(), configfilename, 'exec'), {}, cc)
            if type(cc['platform']) == type('') and cc['platform'].isdigit():
                rv = int(cc['platform'])
        except:
            print('deduce_platform Error:', sys.exc_info()[1])
            raise
        self.platform = rv

    def wheredaq(self, quiet=False):
        """ Locate where the daq is running.
        
        For daqbatch, we use slurm to check if the hutch user is running control_gui.
        """
        daq_host = None
        # Use control_gui job name to locate the running host for the daq
        job_details = self.sbman.get_job_info()
        if 'control_gui' in job_details:
            daq_host = job_details['control_gui']['nodelist']
        
        if not quiet:
            if daq_host is None: 
                print(f'DAQ is not running in {self.hutch}')
            else:
                print(f'DAQ is running on {daq_host}')
        return daq_host
    
    def calldaq(self, subcmd, daq_host=None):
        prog = 'daqbatch'
        cmd = f'pushd {self.scripts_dir}'+' > /dev/null;'
        cmd += f'source {os.path.join(self.scripts_dir, "setup_env.sh")}'+';'
        cmd += f'WHEREPROG=$(which {prog}); set -x; $WHEREPROG {subcmd} {os.path.join(self.scripts_dir,self.cnf_file)}'+'; { set +x; } 2>/dev/null;'
        cmd += f'popd'+' > /dev/null;'
        
        if subcmd == 'restart':
            query_daq_host = self.wheredaq() 
        else:
            query_daq_host = self.wheredaq(quiet=True)

        if daq_host is None:
            daq_host = query_daq_host
            if daq_host is None:
                daq_host = LOCALHOST

        if daq_host == LOCALHOST:
            ret = subprocess.run(cmd, stdout=PIPE, shell=True)
            print(ret.stdout.decode())
        else:
            call_sbatch(cmd, daq_host, self.scripts_dir)
        
        self.waitfor(subcmd)


    def stopdaq(self):
        """ Stop the running daq for the current user.
        Note that daq host is determined by .running file or squeue (daqbatch).
        """
        self.calldaq('stop')

    def startdaq(self, daq_host):
        self.calldaq('start', daq_host=daq_host)

    def restart_daqbatch(self, daq_host):
        st = time.monotonic()
        self.calldaq('restart', daq_host=daq_host)
        en = time.monotonic()
        print(f'took {en-st:.4f}s. for starting the DAQ')

    def restartdaq(self):
        if not self.isvaliduser():
            print(f'Please run the DAQ from the operator account!')
            return
	
        daq_host = LOCALHOST
        # User can use -m to specify the host to run the daq
        for o, a in self.opts:
            if o == '-m':
                daq_host = a
                break
	
        if self.isdaqbatch(quiet=True):
            self.restart_daqbatch(daq_host)
        else:
            self.stopdaq()
            self.startdaq(daq_host)

        
