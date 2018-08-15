

class deviceDict():
    def __init__(self):
        self.deviceDict={}

        self.deviceDict['fastDiode']={}
        self.deviceDict['fastDiode']['pcdssetup-digitized-setup']={}
        self.deviceDict['fastDiode']['pcdssetup-digitized-setup']['device']='Agilent'
        self.deviceDict['fastDiode']['pcdssetup-digitized-setup']['rate']='8 Gs/s'
        self.deviceDict['fastDiode']['pcdssetup-digitized-setup']['purpose']='Fast Diode'

    def getDeviceDict(self):
        return self.deviceDict
