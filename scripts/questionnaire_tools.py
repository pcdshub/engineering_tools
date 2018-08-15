import sys
from psdm_qs_cli import QuestionnaireClient
from deviceDicts import deviceDict
import argparse

class QuestionnaireTools():

    def __init__(self, **kwargs):
        self.qc = QuestionnaireClient(**kwargs)
        self.exp_dict = self.qc.getExpName2URAWIProposalIDs()
        dd = deviceDict()
        self.deviceDict = dd.getDeviceDict()

    def _propRun_from_expname(self, expname):
        try:
            return self.exp_dict[expname],'run%02d'%int(expname[-2:])
        except KeyError:	
            err = '{} is not a valid experiment name'
            raise ValueError(err.format(expname))

    def _isPropname(self, propname):
        for key in self.exp_dict.keys():
            if self.exp_dict[key] == propname:
                return True
        return False

    def _getProposalList(self, runs=[17], instrument=None):
        proposalList=[]
        for key in self.exp_dict.keys():
            try:
                runNo = int(key[-2:])
                if runNo not in runs:
                    continue
                if instrument is not None and keys[:3]!=instrument.lower():
                    continue
                proposalList.append(self.exp_dict[key])
            except:
                pass        
        return proposalList
    
    def _getProposalDetails(self, proposal, run_no,  keyFilter=['pcdssetup']):
        if isinstance(run_no, int):
            run_no='run%02d'%run_no
        if not self._isPropname(proposal):
            print('This is not a proposal %s'%proposal)
            return
        raw = self.qc.getProposalDetailsForRun(run_no, proposal)
        if keyFilter==[]:
            return raw

        filteredDict = {}
        for field in raw.keys():
            for desiredKey in keyFilter:
                if field.find(desiredKey)>=0:
                    filteredDict[field]=raw[field]
        return filteredDict

    def _setProposalDetails(self, runNo, proposal, detailDict):
        for key in detailDict:
            try:
                print('update attribute %s to %s for proposal %s in %s'%(key, detailDict[key], proposal, run_no))
                self.qc.updateProposalAttribute(runNo, proposal, key, detailDict[key])
            except:
                print('failed to update attribute %s to %s for proposal %s in %s'%(key, detailDict[key], proposal, run_no))

    def copyProposal(self, expnameIn, expnameOut):
        try:
            proposalIn, runNoIn = self._propRun_from_expname(expnameIn)
        except:
            print('could not find experiment %s in database'%expnameIn)
        try:
            proposalOut, runNoOut = self._propRun_from_expname(expnameOut)
        except:
            print('could not find experiment %s in database'%expnameOut)

        proposalInDetails = self._getProposalDetails(proposalIn, runNoIn)
        self._setProposalDetails(runNoOut, proposalOut, proposalInDetails)

    def addDeviceToProposal(self, expname, devicename):
        try:
            proposal, runNo = self._propRun_from_expname(expname)
        except:
            print('could not find experiment %s in database'%expname)
            return

        if devicename not in self.deviceDict.keys():
            print('device %s is not in predefined device list, available are:'%devicename)
            print(self.deviceDict.keys)


        addDevice = self.deviceDict[devicename]
        #get current pcds fields from proposal.
        proposalDetails = self._getProposalDetails(proposal, runNo)

        for lineItem in addDevice.keys():
            #first find last kind of this device in current list.
            numNewDevice=-1
            for detail in proposalDetails.keys():
                if detail.find(lineItem)==0:
                    numDev = int(detail.replace('%s-'%lineItem,'').split('-')[0])
                    if numDev>numNewDevice: numNewDevice=numDev+1

            for field in addDevice[lineItem].keys():
                fieldValue = addDevice[lineItem][field]
                fieldName = '%s-%d-%s'%(lineItem,numNewDevice,field)
                print('update field %s to %s for proposal %s in run %s'%(fieldName, fieldValue,proposal, runNo))
                self.qc.updateProposalAttribute(runNo, proposal, fieldName, fieldValue)
                
parser = argparse.ArgumentParser()
parser.add_argument("-f","--fromExp", help="experiment to copy from")
parser.add_argument("-t","--toExp", help="experiment to copy to")
parser.add_argument("-r","--readExp", help="experiment to read CDS tag from")
parser.add_argument("-c","--copy_CDS", help="copy data from CDS tab", action='store_true')
parser.add_argument("-d","--add_device", help="name of device to be added")
parser.add_argument("--print_device", help="name of device to be added")
parser.add_argument("-l","--list_devices", help="list device to be added", action='store_true')
parser.add_argument("--dev", help="connect to dev database", action='store_true')
args = parser.parse_args()


if args.list_devices:
    dd = deviceDict()    
    print('list of available devices: ',dd.getDeviceDict().keys())
    if args.toExp is None:
        sys.exit()

if args.print_device is not None:
    dd = deviceDict()    
    devd = dd.getDeviceDict()
    if args.print_device not in devd.keys():
        print('device %s is not present in device list, avaiable devices are:'%args.print_device)
        print(devd.keys())
    else:
        print(devd[args.print_device])
    if args.toExp is None:
        sys.exit()


kerb_url = 'https://pswww.slac.stanford.edu/ws-kerb/questionnaire/'
kerb_url_dev = 'https://pswww-dev.slac.stanford.edu/ws-kerb/questionnaire/'

#qs =  QuestionnaireTools()
if args.dev:
    qs =  QuestionnaireTools(url=kerb_url_dev)
else:
    qs =  QuestionnaireTools(url=kerb_url)


if args.readExp is not None:
    p,r=qs._propRun_from_expname(args.readExp)
    cdsDict = qs._getProposalDetails(p,r)
    for entry in cdsDict.keys():
        print('%s: \t %s'%(entry, cdsDict[entry]))
    if args.toExp is None:
        sys.exit()

if args.toExp is None:
    toExp=input('we need an experiment to update the questionnaire for')
else:
    toExp = args.toExp

if args.add_device:
    qs.addDeviceToProposal(toExp, devicename=args.add_device)

if args.copy_CDS:
    if args.fromExp is None:
        fromExp = input('experiment to copy CDS data from:')
    else:
        fromExp=args.fromExp
    
    qs.copyProposal(fromExp, toExp)
