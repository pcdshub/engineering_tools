# engineering_tools
A repository of scripts, configuration useful for the PCDS team

## Push updates
```
git push -u origin master
```

## Add Tag
```
git tag -a R{tag} -m '{comment}'

git push -u origin R{tag}
```

## Creating a new release
```
# Clone the source code into a new folder
git clone https://github.com/pcdshub/engineering_tools.git R{tag}
# Enter repository
cd R{Tag}
# checkout tag number
git checkout tags/R{tag}
```

## Updating latest
```
# Go to latest checkout
cd engineering_tools
# Pull latest from master branch
git pull origin master
```

## The scripts

<table>
<tr>
    <td>afs-remote-fix</td>
    <td>
usage: afs-remote-fix<br/>
Will change your afs remotes from e.g.<br/>
origin          /afs/slac.stanford.edu/g/cd/swe/git/repos/package/epics/ioc/common/ims.git<br/>
to</br>
origin          git@github.com:your-username/ioc-common-ims.git<br/>
upstream        git@github.com:pcdshub/ioc-common-ims.git<br/>
    </td>
</tr>

<tr>
    <td>ami_offline_psana</td>
    <td>
usage: ami_offline_psana options<br/>
        <br/>
    We will run ami_offline<br/>
    <br/>
    OPTIONS:<br/>
    -u user (needs to be able to log into the psananeh/feh, if not on psana already)<br/>
    -e EXPNUMBER <br/>
    -R rebinning (binned to 640x640)<br/>
    -n no timetool plugin
    </td>
</tr>

<tr>
    <td>archive-status</td>
    <td>
usage: archive-status [-h] PV <br/>
        <br/>
    Return the status of the specified PV in the archiver.<br/>
    <br/>
    OPTIONS:<br/>
    -h, --help: Show the help message and exit.
    </td>
</tr>

<tr>
    <td>camViewer</td>
    <td>
usage: /reg/g/pcds/engineering_tools/latest/scripts/camViewer options<br/>
    <br/>
    start the viewer for controls cameras<br/>
    <br/>
    OPTIONS:<br/>
    -c|--cam camera name as in camera list or gige #<br/>
    -m|--main bring up the edm screen<br/>
    -r|--reboot reboot the IOC<br/>
    -l|--list print list of cameras<br/>
    -w|--wait # (wait for # hours to ask to renew, default 2 and 12 for GIGEs)<br/>
    -u|--update # update rate limit (default 5)<br/>
    -H|--hutch: use a specific hutches camviewer config file<br/>
    -e|--enable disable camera ioc<br/>
    -d|--disable disable camera ioc<br/>
    -a|--acquire start acquiring images<br/>
    -s|--stop stop acquiring images<br/>
    -n|--cycle cycles acquisition (first stops then starts) <br/>
    </td>
</tr>

<tr>
    <td>check_host</td>
    <td>
Usage:   /reg/g/pcds/engineering_tools/latest/scripts/check_host HOSTNAME<br/>
    <br/>
    Display host info and run some checks.</br>
    </td>
</tr>

<tr>
    <td>configdb_readxtc</td>
    <td>
usage: configdb_readxtc options<br/>
        <br/>
    We will run configdb_readxtc<br/>
    <br/>
    OPTIONS:<br/>
    -u user (needs to be able to log into the psananeh/feh)<br/>
    -e expnumber
    </td>
</tr>

<tr>
    <td>daq_control</td>
    <td>
 daq_control COMMAND TARGET<br/>
     COMMAND : { start, stop, restart, status }<br/>
     TARGET  : { daq, ami }<br/>
     COMMAND : ami<br/>
     TARGET  : { [0], 1 }
    </td>
</tr>

<tr>
    <td>daq_waitwin</td>
    <td>
Waits for the LCLS-I daq windows to load, then exits.
    </td>
</tr>

<tr>
    <td>detector_totals.py</td>
    <td>
Generates a report for the detector group. Reports contains the number of events per detector type gathered from all experiments in a run period.
For example,
<code>detector_totals.py --run_period 20</code> generates the detector total report for run 20
    </td>
</tr>

<tr>
    <td>dev_conda</td>
    <td>
 Source this to activate a pcds conda environment.<br/>
     By default, this activates the latest environment.<br/>
     Use export PCDS_CONDA_VER=VERSION before running to pick a different env.<br/>
     Pick up EPICS environment variable settings just in case user did not
    </td>
</tr>

<tr>
    <td>eloggrabber</td>
    <td>
usage: eloggrabber options<br/>
        <br/>
    start the eloggrabber, by default look at current exp<br/>
    <br/>
    OPTIONS:<br/>
    -e pass in an experiment to look at<br/>
    -x instrument logbook<br/>
    -c controls logbook<br/>
    -u username
    </td>
</tr>
<tr>
    <td>epicsArchChecker</td>
    <td>
usage: epicsArchChecker [-h] [-w] [-s] filepath <br/>
        <br/>
Checks epicsArch files for mismatches of PVs and aliases, missing files, and unconnected PVs.
        <br/>
        <br/>
positional arguments:<br/>
  filepath        Full filepath of the file to check e.g /reg/g/pcds/dist/pds/xpp/misc/epicsArch.txt
        <br/>
        <br/>
optional arguments:<br/>
  -h, --help      show this help message and exit<br/>
  -w, --warnings  Displays: -Pvs and Aliases duplicated. -Pvs with no alias and aliases no Pvs.<br/>
  -s, --status    Displays Pvs not connected.<br/>
    </td>
</tr>
<tr>
    <td>get_curr_exp</td>
    <td>
usage: get_curr_exp options<br/>
        <br/>
    OPTIONS:<br/>
    -l add live status<br/>
    -i/H information for hutch (override autodetection)
    </td>
</tr>

<tr>
    <td>get_hutch_name</td>
    <td>
Returns the hutch name based on the host it is run on. See `get_info` for more information.
    </td>
</tr>

<tr>
    <td>get_info</td>
    <td>
usage: get_info [-h] [--run] [--exp] [--live] [--ended] [--hutch HUTCH]<br/>
                    [--station STATION] [--getHutch] [--gethutch] [--getstation]<br/>
                    [--getbase] [--getinstrument] [--getcnf]<br/>
                    [--files_for_run FILES_FOR_RUN]<br/>
                    [--nfiles_for_run NFILES_FOR_RUN] [--setExp SETEXP]<br/>
    <br/>
    optional arguments:<br/>
      -h, --help            show this help message and exit<br/>
      --run                 get last run<br/>
      --exp                 get experiment name<br/>
      --live                ongoing?<br/>
      --ended               ended<br/>
      --hutch HUTCH         get experiment for hutch xxx<br/>
      --station STATION     optional station for hutch with two daqs, e.g. cxi and mfx<br/>
      --getHutch            get hutch (uppercase)<br/>
      --gethutch            get hutch (lowercase)<br/>
      --getstation          get hutch station (for multiple daqs)<br/>
      --getbase             get base daq name (hutch_station if multiple daqs, otherwise hutch)<br/>
      --getinstrument       get instrument (HUTCH_station if multiple daqs, otherwise hutch)<br/>
      --getcnf              get cnf file name<br/>
      --files_for_run FILES_FOR_RUN<br/>
                            get xtc files for run<br/>
      --nfiles_for_run NFILES_FOR_RUN<br/>
                            get xtc files for run<br/>
      --setExp SETEXP       set experiment name<br/>
    </td>
</tr>

<tr>
    <td>get_lastRun</td>
    <td>
usage: get_lastRun options<br/>
        <br/>
    OPTIONS:<br/>
    -l add live status<br/>
    -i/H information for hutch (override autodetection)
    </td>
</tr>

<tr>
    <td>getPVAliases</td>
    <td>
usage: gatherPVAliases [-h] [-d] patt hutch <br/>
positional arguments: <br/>
  patt           | Regex pattern to match IOCs with.<br/>
                 -->Can match anything in the IOC procmanager object. e.g. "lm2k2" or "mcs2" or "ek9000"<br>
  hutch          | 3 letter hutch code. Use "all" to search through all hutches.<br/>
                 -->Valid arguments: all, aux, cxi, det, hpl, icl, kfe, las, lfe, mec,<br/>
                    mfx, rix, rrl, thz, tmo, tst, txi, ued, xcs, xpp, xrt<br/>

optional arguments:<br/>
  -h, --help     | show this help message and exit<br/>
  -d, --dry_run  | Forces a dry run for the script. No files are saved.<br/>

</tr>

<tr>
    <td>grep_ioc</td>
    <td>
usage: grep_ioc KEYWORD [hutch]<br/>
        hutch can be any of:<br/>
    xpp, xcs, cxi, mfx, mec, xrt, aux, det, fee, hpl, icl, las, lfe, tst, thz, all<br/>
    If no hutch is specified, all hutches will be searched
    </td>
</tr>

<tr>
    <td>grep_more_ioc</td>
    <td>
usage: grep_more_ioc [-h] [-d] patt hutch {print,search} <br/>
     positional arguments: <br/>
     patt                            Regex str to search through iocmanager.cfg<br/>
                                     e.g. 'mcs2', 'lm2k2-atm.*', 'ek9000', 'gige.*'<br/>
     hutch                           3 letter hutch code to search through.<br/>
                                     Use 'all' to search through all hutches.<br/>
                                     Valid arguments: all, aux, cxi, det, hpl, icl, kfe,<br/>
                                     las, lfe, mec, mfx, rix, rrl, thz, tmo, tst, txi, ued,<br/>
                                     xcs, xpp, xrt<br/>
         -h, --help                  Show help message and exit<br/>
         -d, --ignore_disabled       Exclude IOCs based on disabled state <br/>
     Necessary subcommands.<br/>
     Use: grep_more_ioc . all [subcommand] --help for more information
     {print, search}<br/>
         print                       | Prints all the matching IOCs in a dataframe<br/>
         usage: grep_more_ioc patt hutch print [-h] [-c] [-r] [-s] [-y]<br/>
             -h, --help              | Show help message and exit<br/>
             -c, --skip_comments     | Prints IOC.cfg file with comments skipped<br/>
             -r, --release           | Includes the parent IOC release in the dataframe<br/>
             -s, --print_dirs        | Dump child & parent directors to the terminal<br/>
             -y, --print_history     | Dump child IOC's history to terminal, if it exists<br/>
         search                      | Regex-like search of child IOCs<br/>
         usage: grep_more_ioc patt hutch search [-h] [-q] [-o] PATT<br/>
             PATT                    | The regex str to use in the search<br/>
             -h, --help              | Show help message and exit<br/>
             -q, --quiet             | Surpresses file warning for paths that do not exist<br/>
             -o, --only_search       | Skip printing dataframe, only print search results<br/>
    </td>
</tr>

<tr>
    <td>grep_pv</td>
    <td>
     GREP SEARCHES THROUGH ALL IOCs IN /reg/d/iocData/<br/>
     FOR PVs THAT MATCH GIVEN KEYWORD/HANDLE.<br/>
     Ideally, find_pv should be used as it gives a lot more information (but can be slow sometimes)<br/>
    </td>
</tr>

<tr>
    <td>hdf5_to_gif.py</td>
    <td>
     Converts images in hdf5 files created with h5_img_collect to gifs.<br/>
     Specify the path with -p and and how long each frame should last (ms) with -t.<br/>
     Will save to cwd or a specified directory with -d as {original_filename}.gif<br/>
    </td>
</tr>

<tr>
    <td>image_saver</td>
    <td>
     Uses h5_img_collect to save images from a camera in an hdf5 format.<br/>
     Command line arguments -c, -n, -p, and -f to specify camera name, number<br/>
     of images, path to save hdf5 file to, and name to save hdf5 file as.<br/>
     Also can use -g switch to open a GUI with a button that when pressed takes<br/>
     images with specified parameters - can be pressed multiple times. The number<br/>
     of images and the label on each button can be changed within the gui. Images<br/>
     from the gui will be converted into gifs and saved into a (new) ~/gifs directory.<br/>
    </td>
</tr>

<tr>
    <td>ioc-deploy</td>
    <td><pre>
usage: ioc-deploy [-h] [--version] [--name NAME] [--release RELEASE]
&nbsp;                 [--ioc-dir IOC_DIR] [--path-override PATH_OVERRIDE]
&nbsp;                 [--auto-confirm] [--dry-run] [--verbose]
&nbsp;                 [--github_org GITHUB_ORG]
&nbsp;                 {update-perms} ...
&nbsp;
ioc-deploy is a script for building and deploying ioc tags from github.
&nbsp;
It will take one of two different actions: the normal deploy action,
or a write permissions change on an existing deployed release.
&nbsp;
The normal deploy action will create a shallow clone of your IOC in the
standard release area at the correct path and "make" it.
If the tag directory already exists, the script will exit.
&nbsp;
In the deploy action, after making the IOC, we'll write-protect all files
and all directories.
We'll also write-protect the top-level directory to help indicate completion.
&nbsp;
Note that this means you'll need to restore write permissions if you'd like
to rebuild an existing release on a new architecture or remove it entirely.
&nbsp;
Example command:
&nbsp;
"ioc-deploy -n ioc-foo-bar -r R1.0.0"
&nbsp;
This will clone the repository to the default ioc directory and run make using the
currently set EPICS environment variables, then apply write protection.
&nbsp;
With default settings, this will clone
from https://github.com/pcdshub/ioc-foo-bar
to /cds/group/pcds/epics/ioc/foo/bar/R1.0.0
then cd and make and chmod as appropriate.
&nbsp;
If the repository exists but the tag does not, the script will ask if you'd like
to make a new tag and prompt you as appropriate.
&nbsp;
The second action will not do any git or make actions, it will only find the
release directory and change the file and directory permissions.
This can be done with similar commands as above, adding the subparser command,
and it can be done by passing the specific path you'd like to modify
if this is more convenient for you.
&nbsp;
Example commands:
&nbsp;
"ioc-deploy update-perms rw -n ioc-foo-bar -r R1.0.0"
"ioc-deploy update-perms ro -n ioc-foo-bar -r R1.0.0"
"ioc-deploy update-perms rw -p /cds/group/pcds/epics/ioc/foo/bar/R1.0.0"
"ioc-deploy update-perms ro -p /cds/group/pcds/epics/ioc/foo/bar/R1.0.0"
&nbsp;
positional arguments:
&nbsp; {update-perms}        Subcommands (will not deploy):
&nbsp;   update-perms        Use 'ioc-deploy update-perms' to update the write
&nbsp;                       permissions of a deployment. See 'ioc-deploy update-
&nbsp;                       perms --help' for more information.
&nbsp;
optional arguments:
&nbsp; -h, --help            show this help message and exit
&nbsp; --version             Show version number and exit.
&nbsp; --name NAME, -n NAME  The name of the repository to deploy. This is a
&nbsp;                       required argument. If it does not exist on github,
&nbsp;                       we'll also try prepending with 'ioc-common-'.
&nbsp; --release RELEASE, -r RELEASE
&nbsp;                       The version of the IOC to deploy. This is a required
&nbsp;                       argument.
&nbsp; --ioc-dir IOC_DIR, -i IOC_DIR
&nbsp;                       The directory to deploy IOCs in. This defaults to
&nbsp;                       $EPICS_SITE_TOP/ioc, or /cds/group/pcds/epics/ioc if
&nbsp;                       the environment variable is not set. With your current
&nbsp;                       environment variables, this defaults to
&nbsp;                       /reg/g/pcds/epics/ioc.
&nbsp; --path-override PATH_OVERRIDE, -p PATH_OVERRIDE
&nbsp;                       If provided, ignore all normal path-selection rules in
&nbsp;                       favor of the specific provided path. This will let you
&nbsp;                       deploy IOCs or apply protection rules to arbitrary
&nbsp;                       specific paths.
&nbsp; --auto-confirm, --confirm, --yes, -y
&nbsp;                       Skip the confirmation promps, automatically saying yes
&nbsp;                       to each one.
&nbsp; --dry-run             Do not deploy anything, just print what would have
&nbsp;                       been done.
&nbsp; --verbose, -v, --debug
&nbsp;                       Display additional debug information.
&nbsp; --github_org GITHUB_ORG, --org GITHUB_ORG
&nbsp;                       The github org to deploy IOCs from. This defaults to
&nbsp;                       $GITHUB_ORG, or pcdshub if the environment variable is
&nbsp;                       not set. With your current environment variables, this
&nbsp;                       defaults to pcdshub.
&nbsp;
usage: ioc-deploy update-perms [-h] [--name NAME] [--release RELEASE]
&nbsp;                              [--ioc-dir IOC_DIR]
&nbsp;                              [--path-override PATH_OVERRIDE]
&nbsp;                              [--auto-confirm] [--dry-run] [--verbose]
&nbsp;                              {ro,rw}
&nbsp;
Update the write permissions of a deployment. This will make all the files
read-only (ro), or owner and group writable (rw).
&nbsp;
positional arguments:
&nbsp; {ro,rw}               Select whether to make the deployment permissions
&nbsp;                       read-only (ro) or read-write (rw).
&nbsp;
optional arguments:
&nbsp; -h, --help            show this help message and exit
&nbsp; --name NAME, -n NAME  The name of the repository to deploy. This is a
&nbsp;                       required argument. If it does not exist on github,
&nbsp;                       we'll also try prepending with 'ioc-common-'.
&nbsp; --release RELEASE, -r RELEASE
&nbsp;                       The version of the IOC to deploy. This is a required
&nbsp;                       argument.
&nbsp; --ioc-dir IOC_DIR, -i IOC_DIR
&nbsp;                       The directory to deploy IOCs in. This defaults to
&nbsp;                       $EPICS_SITE_TOP/ioc, or /cds/group/pcds/epics/ioc if
&nbsp;                       the environment variable is not set. With your current
&nbsp;                       environment variables, this defaults to
&nbsp;                       /reg/g/pcds/epics/ioc.
&nbsp; --path-override PATH_OVERRIDE, -p PATH_OVERRIDE
&nbsp;                       If provided, ignore all normal path-selection rules in
&nbsp;                       favor of the specific provided path. This will let you
&nbsp;                       deploy IOCs or apply protection rules to arbitrary
&nbsp;                       specific paths.
&nbsp; --auto-confirm, --confirm, --yes, -y
&nbsp;                       Skip the confirmation promps, automatically saying yes
&nbsp;                       to each one.
&nbsp; --dry-run             Do not deploy anything, just print what would have
&nbsp;                       been done.
&nbsp; --verbose, -v, --debug
&nbsp;                       Display additional debug information.
    </pre></td>
</tr>

<tr>
    <td>iocmanager</td>
    <td>
iocmanager [hutch]<br/>
    <br/>
    Control status of all IOCs running in a particular hutch in an interactive GUI.<br/>
    Current hutch is used if not provided.
    </td>
</tr>

<tr>
    <td>ioctool</td>
    <td>
usage: ioctool &lt;ioc&gt;|&lt;pv&gt; [option]<br/>
        <br/>
    Script that returns information about an ioc given its name or a PV it hosts<br/>
        <br/>
    default option  is 'name', list of options:<br/>
    status : print power status of machine, try to ping interfaces<br/>
    name     : returns the name of the ioc<br/>
    dir     : returns the path to the directory the ioc is running from<br/>
    cddir  :opens the directory the ioc is running from (start with "source" before calling script with this option)<br/>
    cfg  : returns the the file name of the ioc .cfg (or st.cmd)<br/>
    less: opens the ioc .cfg (or st.cmd) in less<br/>
    cat  : opens the ioc .cfg (or st.cmd) in cat <br/>
    data : returns the path of the appropriate iocData directory if it exists<br/>
    autosave : opens the most recent autosave file in less <br/>
    archive  : opens the most recent archive file in less <br/>
    log      : opens the most recent log file in less<br/>
    telnet : starts a telnet session with the ioc<br/>
    pvs	   : opens the IOC.pvlist file in less<br/>
    </td>

</tr>

<tr>
    <td>ipmConfigEpics</td>
    <td>
usage: ipmConfigEpics [-b boxname] [-H hutch] [-d] [-h] [-l]<br/>
          -b: specify boxname to view<br/>
      -H: specify a hutch to use, overriding the automated selection<br/>
      -d: fix issues with Bld Damage (likely camera IOC w/plugins on same machine)<br/>
      -h: display this help text<br/>
      -l: list available boxnames
    </td>
</tr>

<tr>
    <td>kinit_helper</td>
    <td>
usage: kinit_helper<br/>
    Defines two functions - kauth and afsauth.<br/>
    kauth will create a new kerberos token, renew an existing one, or do nothing if a
    valid token exists.<br/>
    afsauth will check that the	user and host are able to access afs; if so, and an afs
    token doesn't already exist, kauth will be called and a new afs token will be made.<br/>
    By default, calls afsauth.
    </td>
</tr>

<tr>
    <td>makepeds</td>
    <td>
usage: makepeds options<br/>
        <br/>
    Make a pedestal file for offline use<br/>
    <br/>
    OPTIONS:<br/>
    -u user (needs to be able to log into the psananeh/feh)<br/>
    -r runnumber for pedestal<br/>
    -e EXPNAME in case you do not want pedestals for the ongoing experiment<br/>
    -J make pedestals for Jungfrau (default only cspad/EPIX detectors)<br/>
    -j make pedestals for Jungfrau - 3 run version(default only cspad/EPIX detectors)<br/>
    -O make pedestals for Opals (default only cspad/EPIX detectors)<br/>
    -Z make pedestals for Zyla (default only cspad/EPIX detectors)<br/>
    -p TEXT: add <text> to elog post<br/>
    -c EVTCODE X use events with eventcode X set<br/>
    -n # : if you have created a noise file, then write pixel mask file for pixels with noise above #sigma<br/>
    -N # : use this number of events (default 1000)<br/>
    -D : dark run for XTCAV<br/>
    -L : lasing off run for XTCAV<br/>
    -v STR: validity range (if not run#-end, e.g. 123-567 or 123-end)<br/>
    -l: do NOT send to batch queue<br/>
    -F : use the FFB (default if no experiment is passed)<br/>
    -g : run on an FFB batch node<br/>
    -f : full epix10k charge injection run<br/>
    -C # : if noise filecreated, write pixel mask file for pixels with noise below xxx (currently integer only...)<br/>
    -m # : write pixel mask file for pixels with pedestal below xxx (currently integer only...)<br/>
    -x # : write pixel mask file for pixels with pedestal above xxx (currently integer only...)<br/>
    -i start calibman. -r 0: show all darks, -r n: show runs (n-25) - 25<br/>
    -d give path for alternative calibdir
    </td>
</tr>

<tr>
    <td>makepeds_psana</td>
    <td>
usage: makepeds_psana options<br/>
        <br/>
    Make a pedestal file<br/>
    <br/>
    OPTIONS:<br/>
    -r runnumber for pedestal<br/>
    -e EXPNAME in case you do not want pedestals for the ongoing experiment<br/>
    -H HUTCH in case you do not pass an experiment name<br/>
    -Z pedestal for zyla<br/>
    -O make pedestals for Opals<br/>
    -J pedestal for jungfrau (needs first of set of 3 runs!)<br/>
    -D : dark run for XTCAV<br/>
    -L : lasing off run for XTCAV (-b specifies the number of assumed bunches, def 1)<br/>
    -l : donot send to batch queue<br/>
    -F : use FFB<br/>
    -f : full epix10k charge injection run<br/>
    -v STR: validity range (if not run#-end, e.g. 123-567 or 123-end)<br/>
    -N # : use this number of events (default 1000)<br/>
    -n # : if noise filecreated, write pixel mask file for pixels with noise above xxx (currently integer only...)<br/>
    -C # : if noise filecreated, write pixel mask file for pixels with noise below xxx (currently integer only...)<br/>
    -m # : write pixel mask file for pixels with pedestal below xxx (currently integer only...)<br/>
    -x # : write pixel mask file for pixels with pedestal above xxx (currently integer only...)<br/>
    -c EVTCODE X use events with eventcode X set<br/>
    -i start calibman. -r 0: show all darks, -r n: show runs (n-25) - 25<br/>
    -d give path for alternative calibdir<br/>
    -t : test, do not deploy.<br/>
    -y : when specify cuts for status mask, apply those for epix100.
    </td>
</tr>

<tr>
    <td>motor-expert-screen</td>
    <td>
usage: motor-expert-screen options MOTOR_PV_BASENAME<br/>
        <br/>
    Start an EDM for the specified motor.<br/>
    Attempts to choose the correct type.<br/>
    <br/>
    OPTIONS:<br/>
    -h shows the usage information
    </td>
</tr>

<tr>
    <td>motor-typhos</td>
    <td>
usage: motor-typhos options MOTOR_PV_BASENAME<br/>
        <br/>
    Start a typhos screen for the specified motor.<br/>
    Attempts to choose the correct type.<br/>
    <br/>
    OPTIONS:<br/>
    -h shows the usage information
    </td>
</tr>

<tr>
    <td>motorInfo</td>
    <td>
usage: motorInfo MOTOR_PV (motor_pv_2/autosave/archive/pmgr_diff/pmgr_save) OPT<br/>
        <br/>
    If given two motors, compare their settings<br/>
    If given autosave as second argument, compare the current settings to the autosaved values: differences will be printed<br/>
    If given archive, the archive values will be printed for the last week. If only the base PV is given, extra arguments will be needed<br/>
    <br/>
    OPTIONS:<br/>
    -h shows the usage information<br/>
    -f fields to use as a comma separated list (default: use all autosave values)<br/>
    -s start time for archiver info (YYYY/MM/DD HH:MM:SS)<br/>
    -e end time for archiver info (YYYY/MM/DD HH:MM:SS)
    </td>
</tr>

<tr>
    <td>pcds_conda</td>
    <td>
 Source this to activate a pcds conda environment.<br/>
     By default, this activates the latest environment.<br/>
     Use export PCDS_CONDA_VER=VERSION before running to pick a different env.<br/>
     Pick up EPICS environment variable settings just in case user did not
    </td>
</tr>

<tr>
    <td>pgpwave8_upgrade</td>
    <td>

     usage $0 -i IOCNAME [-d DEVICE] [-r] [-p FIRMWARE_PATH]<br/>
     <br/>
     Read or upgrade the firmware version of a pgpwave8 given its ioc.<br/>
     <br/>
    -i The ioc whose pgpwave8's firmware should be upgraded.<br/>
    -d The path to the device, defaulting to /dev/datadev_0.<br/>
    -r Print the firmware version only. Cannot be used with -p.<br/>
    -p The path to the mcs file containing the new firmware.<br/>
    Cannot be used with -r. Some firmware images can be found<br/>
    in /cds/group/pcds/package/wave8/images. If -r and -p are not provided,<br/>
    user will be prompted if they want to use<br/>
    /cds/group/pcds/package/wave8/images/latest as the new firmware.

EOF
    </td>
</tr>

<tr>
    <td>pkg_release</td>
    <td>
 Checks out a package from the pcdshub github at a particular tag.<br/>
     Does not update "latest" softlinks, these are inconsistent between packages.<br/>
     Make sure your tag exists before running.
    </td>
</tr>

<tr>
    <td>pmgr</td>
    <td>
 pmgr [hutch] [--debug] [--applyenable]<br/>
     --debug  : Displays the debug button, which prints out any edits made<br/>
     --applyenable	 : Displays the apply all button, which applies settings to all motors
    </td>
</tr>

<tr>
    <td>pydev_env</td>
    <td>
 Source this file to activate a development environment based on the latest<br/>
     shared environment and on past calls to pydev_register
    </td>
</tr>

<tr>
    <td>pydev_register</td>
    <td>
 Use this script to register development packages so that they will be<br/>
     available when you source pydev_env
    </td>
</tr>

<tr>
    <td>pyps-deploy</td>
    <td>
usage: pyps-deploy [-h] -r RELEASE -c CONDA [--repo REPO] [--app-bin APP_BIN] app <br/>
    <br/>
    Sets up a pyps/apps deployment for a particular github python package. This<br/>
    will create an executable under .../pyps/apps/APP-NAME/RELEASE/APP-NAME<br/>
    and repoint the symbolic link at .../pyps/apps/APP-NAME/latest to the new<br/>
    release folder.<br/>
    <br/>
    positional arguments:<br/>
      app                   Name of the app to deploy<br/>
    <br/>
    optional arguments:<br/>
      -h, --help            show this help message and exit<br/>
      -r RELEASE, --release RELEASE<br/>
                            App version<br/>
      -c CONDA, --conda CONDA<br/>
                            Conda environment name<br/>
      --repo REPO           Clone this repo and mask the environment package. Use<br/>
                            this when you have only a small change that does not<br/>
                            need a full environment release.<br/>
      --app-bin APP_BIN     Use in conjunction with --repo arg when the launcher<br/>
                            is not in the bin directory
    </td>
</tr>

<tr>
    <td>questionnaire_tools</td>
    <td>
usage: questionnaire_tools [-h] [-f FROMEXP] [-t TOEXP] [-r READEXP] [-c]<br/>
                               [-d ADD_DEVICE] [-l] [-p PRINT_DEVICE] [--dev]<br/>
                               [--experimentList] [--propList]<br/>
    <br/>
    optional arguments:<br/>
      -h, --help            show this help message and exit<br/>
      -f FROMEXP, --fromExp FROMEXP<br/>
                            experiment to copy from<br/>
      -t TOEXP, --toExp TOEXP<br/>
                            experiment to copy to<br/>
      -r READEXP, --readExp READEXP<br/>
                            experiment to read CDS tag from<br/>
      -c, --copy_CDS        copy data from CDS tab<br/>
      -d ADD_DEVICE, --add_device ADD_DEVICE<br/>
                            name of device to be added<br/>
      -l, --list_devices    list device to be added<br/>
      -p PRINT_DEVICE, --print_device PRINT_DEVICE<br/>
                            print data for device<br/>
      --dev                 connect to dev database<br/>
      --experimentList      list of experiments<br/>
      --propList            list of proposals<br/>
    </td>
</tr>

<tr>
    <td>restartdaq</td>
    <td>
usage: restartdaq options<br/>
        <br/>
    OPTIONS:<br/>
    -w sort windows after start<br/>
    -p select partition (same as used last)<br/>
    -s silent (do not email jana)<br/>
    -C [cnf] : <b>(FOR LCLS2 Hutches)</b> Specify a CNF to run. E.g. qrix.py or crix.py
    </td>
</tr>

<tr>
    <td>serverStat</td>
    <td>
usage: serverStat servername options<br/>
        <br/>
    Script to check status of servers & reboot/power cycle them<br/>
    <br/>
    SIGNATURE:<br/>
    serverStat SERVERNAME [command]<br/>
    <br/>
    default command is 'status', list of commands:<br/>
    status : print power status of machine, try to ping interfaces<br/>
    on     : power machine on<br/>
    off    : power machine off<br/>
    cycle  : power cycle machine, wait a few second in off state<br/>
    reset  : reset machine (ideally try that before power cycling)<br/>
    console: open the ipmi console where possible<br/>
    expert : display info and run checks on server
    </td>
</tr>

<tr>
    <td>ssh-agent-helper</td>
    <td>
usage: source ssh-agent-helper<br/><br/>
Helper script for starting the ssh agent if needed and doing an ssh-add -t 12h.
This will let anyone smoothly run github/ssh related scripts without multiple password prompts.
An ssh-agent process started by using this script will be automatically closed on logout.
<br/><br/>
This script is intended to be sourced.
Sourcing this script lets ssh-agent set the proper environment variables it needs to run properly.
    </td>
</tr>

<tr>
    <td>startami</td>
    <td>
usage: startami options<br/>
        <br/>
    we are starting another ami session here<br/>
    <b>This script restarts AMI1 in LCLS1 hutches and AMI2 in LCLS2 hutches</b><br/>
    <br/>
    OPTIONS:<br/>
    -s: stop the ami client current running on this machine<br/>
    -c: config file you'd like to use (i.e. cxi_test.cnf)
    </td>
</tr>

<tr>
    <td>stopami</td>
    <td>
Kill an AMI process running in the current hutch.<br/>
<b>This script stops AMI1 in LCLS1 hutches and AMI2 in LCLS2 hutches</b>
    </td>
</tr>

<tr>
    <td>stopdaq</td>
    <td>
Stop the daq in the current hutch.
    </td>
</tr>

<tr>
    <td>takepeds</td>
    <td>
usage: takepeds <br/>
Takes a run with dark images for use in pedestals, and posts to the elog.
    </td>
</tr>

<tr>
    <td>verify-hutch</td>
    <td>
usage: verify-hutch hutch <br/>
Verifies that the passed argument is a known hutch, exit 0 for success and exit 1 for failure.
    </td>
</tr>

<tr>
    <td>wheredaq</td>
    <td>
Discover what host is running the daq in the current hutch, if any.
    </td>
</tr>

<tr>
    <td>wherepsana</td>
    <td>
Usage: where_psana [-h] [-c  CONFIG] [-d DETAIL]<br/>
Checks where we have shared memory servers for psana running and could run psana jobs.<br/>
Optional arguments:<br/>
-h      Show usage<br/>
-c      Pick a specific DAQ config file rather than automatically selecting current hutch's file<br/>
-d      Also show information about dss node mapping<br/>
    </td>
</tr>

<tr>
    <td> set_gem_timing</td>
    <td>
    Usage: set_gem_timing [SC or NC]
    </td>
</tr>

</table>
