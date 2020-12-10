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
    <td>ami_offline_psana</td>
    <td>
usage: ami_offline_psana options<br/>
        <br/>
    We will run ami_offline<br/>
    <br/>
    OPTIONS:<br/>
    -u user (needs to be able to log into the psananeh/feh, if not on psana already)<br/>
    -e <expnumber> <br/>
    -R rebinning (binned to 640x640)<br/>
    -n no timetool plugin
    </td>
</tr>

<tr>
    <td>camViewer</td>
    <td>
 find_pv: use find_pv to get to the sysreset PV of the IOC for rebooting.<br/>
     --> does not work. Need to know more. Maybe just use in case of gige, assuming naming convention.<br/>
     from EDM_LAUNCH: grep that cmd file for 'export IOC_PV'!!!
    </td>
</tr>

<tr>
    <td>check_host</td>
    <td>
(TODO)
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
 daq_control <command> <target><br/>
     <command> : { start, stop, restart, status }<br/>
     <target>  : { daq, ami }<br/>
     <command> : ami<br/>
     <target>  : { [0], 1 }
    </td>
</tr>

<tr>
    <td>daq_waitwin</td>
    <td>
(TODO)
    </td>
</tr>

<tr>
    <td>dev_conda</td>
    <td>
 Source this to activate a pcds conda environment.<br/>
     By default, this activates the latest environment.<br/>
     Use export PCDS_CONDA_VER=<version> before running to pick a different env.<br/>
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
(TODO)
    </td>
</tr>

<tr>
    <td>get_info</td>
    <td>
(TODO)
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
    <td>gige</td>
    <td>
(TODO)
    </td>
</tr>

<tr>
    <td>grep_ioc</td>
    <td>
usage: grep_ioc <keyword> [hutch]<br/>
        hutch can be any of:<br/>
    xpp, xcs, cxi, mfx, mec, xrt, aux, det, fee, hpl, icl, las, lfe, tst, thz, all<br/>
    If no hutch is specified, all hutches will be searched
    </td>
</tr>

<tr>
    <td>grep_pv</td>
    <td>
##################################################<br/>
     GREP SEARCHES THROUGH ALL IOCs IN /reg/d/iocData/<br/>
     FOR PVs THAT MATCH GIVEN KEYWORD/HANDLE.<br/>
    ##################################################
    </td>
</tr>

<tr>
    <td>iocmanager</td>
    <td>
PATH=$PATH:$DIR
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
    <td>makepeds</td>
    <td>
usage: makepeds options<br/>
        <br/>
    Make a pedestal file for offline use<br/>
    <br/>
    OPTIONS:<br/>
    -u user (needs to be able to log into the psananeh/feh)<br/>
    -r runnumber for pedestal<br/>
    -e <expname> in case you do not want pedestals for the ongoing experiment<br/>
    -J make pedestals for Jungfrau (default only cspad/EPIX detectors)<br/>
    -j make pedestals for Jungfrau - 3 run version(default only cspad/EPIX detectors)<br/>
    -O make pedestals for Opals (default only cspad/EPIX detectors)<br/>
    -Z make pedestals for Zyla (default only cspad/EPIX detectors)<br/>
    -p <text>: add <text> to elog post<br/>
    -c <evtcode x> use events with eventcode <x> set<br/>
    -n # : if you have created a noise file, then write pixel mask file for pixels with noise above #sigma<br/>
    -N # : use this number of events (default 1000)<br/>
    -D : dark run for XTCAV<br/>
    -L : lasing off run for XTCAV<br/>
    -v <str>: validity range (if not run#-end, e.g. 123-567 or 123-end)<br/>
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
    -e <expname> in case you do not want pedestals for the ongoing experiment<br/>
    -H <hutch> in case you do not pass an experiment name<br/>
    -Z pedestal for zyla<br/>
    -O make pedestals for Opals<br/>
    -J pedestal for jungfrau (needs first of set of 3 runs!)<br/>
    -D : dark run for XTCAV<br/>
    -L : lasing off run for XTCAV (-b specifies the number of assumed bunches, def 1)<br/>
    -l : donot send to batch queue<br/>
    -F : use FFB<br/>
    -f : full epix10k charge injection run<br/>
    -v <str>: validity range (if not run#-end, e.g. 123-567 or 123-end)<br/>
    -N # : use this number of events (default 1000)<br/>
    -n # : if noise filecreated, write pixel mask file for pixels with noise above xxx (currently integer only...)<br/>
    -C # : if noise filecreated, write pixel mask file for pixels with noise below xxx (currently integer only...)<br/>
    -m # : write pixel mask file for pixels with pedestal below xxx (currently integer only...)<br/>
    -x # : write pixel mask file for pixels with pedestal above xxx (currently integer only...)<br/>
    -c <evtcode x> use events with eventcode <x> set<br/>
    -i start calibman. -r 0: show all darks, -r n: show runs (n-25) - 25<br/>
    -d give path for alternative calibdir<br/>
    -t : test, do not deploy.<br/>
    -y : when specify cuts for status mask, apply those for epix100.
    </td>
</tr>

<tr>
    <td>motor-expert-screen</td>
    <td>
usage: motor-expert-screen options <motor_pv_basename><br/>
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
usage: motor-typhos options <motor_pv_basename><br/>
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
usage: motorInfo <motor_pv> <motor_pv_2/autosave/archive/pmgr_diff/pmgr_save> <opt><br/>
        <br/>
    If given two motors, compare their settings<br/>
    If given autosave as second argument, compare the current settings to the autosaved values: differences will be printed<br/>
    If given archive, the archive values will be printed for the last week. If only the base PV is given, extra arguments will be needed<br/>
    <br/>
    OPTIONS:<br/>
    -h shows the usage information<br/>
    -f fields to use as a comma separated list <default: use all autosave values><br/>
    -s start time for archiver info <YYYY/MM/DD HH:MM:SS><br/>
    -e end time for archiver info <YYYY/MM/DD HH:MM:SS>
    </td>
</tr>

<tr>
    <td>pcds_conda</td>
    <td>
 Source this to activate a pcds conda environment.<br/>
     By default, this activates the latest environment.<br/>
     Use export PCDS_CONDA_VER=<version> before running to pick a different env.<br/>
     Pick up EPICS environment variable settings just in case user did not
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
     --debug	: Displays the debug button, which prints out any edits made<br/>
     --applyenable	: Displays the apply all button, which applies settings to all motors
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
(TODO)
    </td>
</tr>

<tr>
    <td>questionnaire_tools</td>
    <td>
(TODO)
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
    -s silent (do not email jana)
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
    serverStat <servername> [command]<br/>
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
    <td>startami</td>
    <td>
usage: startami options<br/>
        <br/>
    we are starting another ami session here<br/>
    <br/>
    OPTIONS:<br/>
    -s: stop the ami client current running on this machine<br/>
    -c: config file you'd like to use (i.e. cxi_test.cnf)
    </td>
</tr>

<tr>
    <td>stopami</td>
    <td>
(TODO)
    </td>
</tr>

<tr>
    <td>stopdaq</td>
    <td>
(TODO)
    </td>
</tr>

<tr>
    <td>wheredaq</td>
    <td>
(TODO)
    </td>
</tr>

<tr>
    <td>wherepsana</td>
    <td>
(TODO)
    </td>
</tr>

</table>
