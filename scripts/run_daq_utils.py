import os,sys,time
from daq_utils import DaqManager
import getopt

help_messages = {
        'wheredaq': 'Discover what host is running the daq in the current hutch, if any.',
        'stopdaq': 'Stop the daq in the current hutch.',
        'restartdaq': 'Verify requirements for running the daq then stop and start it.',
        'isdaqbatch': "Determine if the current user's hutch uses daqbatch",
        }

if __name__ == "__main__":
    commands = ['wheredaq', 'stopdaq', 'restartdaq', 'isdaqbatch']
    opts, args = getopt.getopt(sys.argv[2:], 'hm:dv', ["help","dss"])
    cmd = sys.argv[1]
    if cmd not in commands:
        print(f'Unsupported command {cmd}')
        raise
    for o, a in opts:
        if o in ("-h", "--help"):
            print(help_messages[cmd])
            exit()

    daqman = DaqManager(opts)
    func = getattr(daqman, cmd)
    result = func()

