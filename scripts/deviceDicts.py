from copy import deepcopy

class deviceDict():
    def __init__(self, hutch=None):
        self.deviceDict={}
        #
        fastDiode={}
        fastDiode['device']='Agilent'
        fastDiode['rate']='8 Gs/s'
        fastDiode['purpose']='Fast Diode'
        #
        timeToolOpal={}
        timeToolOpal['type']='Opal-1k'
        timeToolOpal['record']='DAQ'
        timeToolOpal['trigger']='120'
        timeToolOpal['purpose']='Time Tool'
        #
        self.deviceDict['fastDiode']={}
        self.deviceDict['fastDiode']['pcdssetup-digitized-setup']=[]
        self.deviceDict['fastDiode']['pcdssetup-digitized-setup'].append(fastDiode)
        #
        #
        #
        self.deviceDict['JJslit']={}
        self.deviceDict['JJslit']['pcdssetup-motors-setup']=[]
        for motorName in {'jj_vg', 'jj_hg', 'jj_vo', 'jj_ho'}:
            deviceMotor={}            
            if motorName=='jj_vg': deviceMotor['purpose']='vertical gap'
            elif motorName=='jj_hg': deviceMotor['purpose']='horizontal gap'
            elif motorName=='jj_vo': deviceMotor['purpose']='vertical offset'
            elif motorName=='jj_ho': deviceMotor['purpose']='horizontal offset'
            deviceMotor['name']=motorName
            deviceMotor['stageidentity']=motorName
            if hutch is not None:
                deviceMotor['pvbase']='%s:USR:MMS:'%hutch.upper()
            self.deviceDict['JJslit']['pcdssetup-motors-setup'].append(deviceMotor)
        #
        #
        #
        self.deviceDict['vonHamos_small']={}
        self.deviceDict['vonHamos_small']['pcdssetup-motors-setup']=[]
        self.deviceDict['vonHamos_small']['pcdssetup-areadet-setup']=[]
        epixDet={}
        epixDet['type']='Epix100'
        epixDet['alias']='epix_1'
        self.deviceDict['vonHamos_small']['pcdssetup-areadet-setup'].append(epixDet)
        for motorName in {'vHs_v', 'vHs_h', 'vHs_r'}:
            deviceMotor['name']=motorName
            deviceMotor['stageidentity']=motorName
            if motorName=='vHs_v': deviceMotor['purpose']='common vertical'
            elif motorName=='vHs_h': deviceMotor['purpose']='common horizontal'
            elif motorName=='vHs_r': deviceMotor['purpose']='common rotation'
            if hutch is not None:
                deviceMotor['pvbase']='%s:USR:MMS:'%hutch.upper()
            self.deviceDict['vonHamos_small']['pcdssetup-motors-setup'].append(deviceMotor)
        #
        #
        #
        self.deviceDict['vonHamos']={}
        self.deviceDict['vonHamos']['pcdssetup-motors-setup']=[]
        self.deviceDict['vonHamos']['pcdssetup-areadet-setup']=[]
        epixDet={}
        epixDet['type']='Epix100'
        epixDet['alias']='epix_1'
        self.deviceDict['vonHamos']['pcdssetup-areadet-setup'].append(epixDet)
        for motorName in {'vH_v', 'vH_h', 'vH_r'}:
            deviceMotor['name']=motorName
            deviceMotor['stageidentity']=motorName
            if motorName=='vHs_v': deviceMotor['purpose']='common vertical'
            elif motorName=='vHs_h': deviceMotor['purpose']='common horizontal'
            elif motorName=='vHs_r': deviceMotor['purpose']='common rotation'
            if hutch is not None:
                deviceMotor['pvbase']='%s:USR:MMS:'%hutch.upper()
            self.deviceDict['vonHamos']['pcdssetup-motors-setup'].append(deviceMotor)
        #
        #
        #
        self.deviceDict['CXI_stdCfg']={}
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup']=[]
        motor={}
        motor['purpose']='Laser incoupling mirror X'
        motor['name']='laser_incoupling_mirror_x'
        motor['stageidentity']='VT-50'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:USR:MMS:25'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'Laser incoupling mirror Y'
        motor['name'] = 'laser_incoupling_mirror_y'
        motor['stageidentity'] = 'VT-50'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:USR:MMS:28'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'Laser incoupling mirror Z'
        motor['name'] = 'laser_incoupling_mirror_z'
        motor['stageidentity'] = 'VT-50'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:USR:MMS:27'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'Laser incoupling lens X'
        motor['name'] = 'laser_incoupling_lens_x'
        motor['stageidentity'] = 'VT-21'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:USR:MMS:26'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'sc1 laser mirror yaw'
        motor['name'] = 'laser_sc1mirror1_yaw'
        motor['stageidentity'] = 'pico'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:LAS:PIC:03'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'sc1 laser mirror pitch'
        motor['name'] = 'laser_sc1mirror1_pitch'
        motor['stageidentity'] = 'pico'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:LAS:PIC:02'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'Side Illumination X'
        motor['name'] = 'illumination_x'
        motor['stageidentity'] = 'VT-21'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MMS:09'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'Side Illumination Y'
        motor['name'] = 'illumination_y'
        motor['stageidentity'] = 'VT-21'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:USR:MMS:17'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'Side Illumination Z'
        motor['name'] = 'illumination_z'
        motor['stageidentity'] = 'VT-21'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:USR:MMS:19'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'Sample Diode'
        motor['name'] = 'sample_x'
        motor['stageidentity'] = 'VT-50 (long)'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MMS:02'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 fast diode piezo motors'
        motor['name'] = 'sc1diode_y'
        motor['stageidentity'] = 'piezo'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MZM:09'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 Questar zoom'
        motor['name'] = 'Sc1Questar_zoom'
        motor['stageidentity'] = 'Questar'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MMS:01'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 Questar X'
        motor['name'] = 'Sc1Questar_x'
        motor['stageidentity'] = 'VT-21'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MMS:03'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 Questar Y'
        motor['name'] = 'Sc1Questar_y'
        motor['stageidentity'] = 'VT-21'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MMS:04'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 Objective X'
        motor['name'] = 'sc1objective_x'
        motor['stageidentity'] = 'VT-50'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MMS:06'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 Objective Y'
        motor['name'] = 'sc1objective_y'
        motor['stageidentity'] = 'VT-50'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MMS:05'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 Objective top z'
        motor['name'] = 'sc1objective_z1'
        motor['stageidentity'] = 'VT-50'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MMS:08'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 Objective bot z'
        motor['name'] = 'sc1objective_z2'
        motor['stageidentity'] = 'VT-50'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MMS:07'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 PI1 X'
        motor['name'] = 'pi1_x'
        motor['stageidentity'] = 'IMS smart motor'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:PI1:MMS:01'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 PI1 Y'
        motor['name'] = 'pi1_y'
        motor['stageidentity'] = 'IMS smart motor'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:PI1:MMS:02'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 PI1 Z'
        motor['name'] = 'pi1_z'
        motor['stageidentity'] = 'IMS smart motor'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:PI1:MMS:03'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 PI1 Fine X'
        motor['name'] = 'pi1_fine_x'
        motor['stageidentity'] = 'IMS smart motor'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:USR:MMS:01'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 PI1 Fine Y'
        motor['name'] = 'pi1_fine_y'
        motor['stageidentity'] = 'IMS smart motor'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:USR:MMS:02'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 PI1 Fine Z'
        motor['name'] = 'pi1_fine_z'
        motor['stageidentity'] = 'IMS smart motor'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:USR:MMS:03'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 LED'
        motor['name'] = 'sc1led_stick'
        motor['stageidentity'] = 'IMS smart motor'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MMS:18'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 Aperture 1 X'
        motor['name'] = 'sc1ap1_x'
        motor['stageidentity'] = 'piezo'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MZM:05'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 Aperture 1 Y'
        motor['name'] = 'sc1ap1_y'
        motor['stageidentity'] = 'piezo'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MZM:06'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 Aperture 2 X'
        motor['name'] = 'sc1ap2_x'
        motor['stageidentity'] = 'piezo'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor[' pvbase'] = 'CXI:SC1:MZM:07'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 Aperture 2 Y'
        motor['name'] = 'sc1ap2_y'
        motor['stageidentity'] = 'piezo'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MZM:08'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 Ta Jaws +X blade'
        motor['name'] = 'sc1ap0_s'
        motor['stageidentity'] = 'piezo'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MZM:01'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 Ta Jaws -X blade'
        motor['name'] = 'sc1ap0_n'
        motor['stageidentity'] = 'piezo'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MZM:14'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 Ta Jaws +Y blade'
        motor['name'] = 'sc1ap0_u'
        motor['stageidentity'] = 'piezo'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MZM:02'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'SC1 Ta Jaws -Y blade'
        motor['name'] = 'sc1ap0_d'
        motor['stageidentity'] = 'piezo'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:SC1:MZM:04'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'Sample Y'
        motor['name'] = 'sample_y'
        motor['stageidentity'] = 'VT-50'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:USR:MMS:18'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'Sample Z'
        motor['name'] = 'sample_z'
        motor['stageidentity'] = 'VT-50'
        motor['invac'] = 'Yes'
        motor['location'] = 'CXI SC1'
        motor['pvbase'] = 'CXI:USR:MMS:20'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor); motor={}
        motor['purpose'] = 'Newport Rotational Motor'
        motor['name'] = 'opo_wp'
        motor['stageidentity'] = 'Newport'
        motor['connection'] = 'On movable optical table for OPO'
        motor['pvbase'] = 'CXI:USR:MMN:'
        self.deviceDict['CXI_stdCfg']['pcdssetup-motors-setup'].append(motor)

        self.deviceDict['CXI_stdCfg']['pcdssetup-digitized-setup']=[]
        self.deviceDict['CXI_stdCfg']['pcdssetup-digitized-setup'].append(fastDiode)

        self.deviceDict['CXI_stdCfg']['pcdssetup-areadet-setup']=[]
        det={}
        det['type']='CSPAD-2.3M'
        det['alias']='DscCsPad'
        det['record']='DSC rack'
        self.deviceDict['CXI_stdCfg']['pcdssetup-areadet-setup'].append(det)

        self.deviceDict['CXI_stdCfg']['pcdssetup-camera-setup']=[]
        det=deepcopy(timeToolOpal)
        det['alias']='TimeTool'
        self.deviceDict['CXI_stdCfg']['pcdssetup-camera-setup'].append(det); det={}
        det['type']='Opal-1k'
        det['alias']='Sc1Questar'
        det['record']='DAQ'
        det['trigger']='120'
        det['purpose']='Questar camera'
        self.deviceDict['CXI_stdCfg']['pcdssetup-camera-setup'].append(det); det={}
        det['type']='Uniq'
        det['record']='vewing only'
        det['trigger']='free run'
        det['purpose']='Side Viewing'
        self.deviceDict['CXI_stdCfg']['pcdssetup-camera-setup'].append(det)

        self.deviceDict['CXI_stdCfg']['pcdssetup-trig-setup']=[]
        trigger={}
        trigger['delay']='894285.7'
        trigger['width']='1000'
        trigger['pvbase']='CXI:R52:EVR:01:TRIG2'
        trigger['purpose']='X-ray simulator EVR for Acqiris'
        trigger['polarity']='positive'
        self.deviceDict['CXI_stdCfg']['pcdssetup-camera-setup'].append(trigger)
        trigger['eventcode']='40;'
        trigger['delay']='TBD'
        trigger['purpose']='X-ray simulator EVR for LeCroy'
        trigger.pop('width',None)
        trigger.pop('polarity',None)
        trigger.pop('pvbase',None)
        self.deviceDict['CXI_stdCfg']['pcdssetup-camera-setup'].append(trigger)


    def getDeviceDict(self):
        return self.deviceDict
