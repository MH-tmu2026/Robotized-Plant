#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file Soilmoisture_Sensor.py
 @brief Soil moisture sensor compornent
 @date $Date$


"""

import sys
import time
from grove.adc import ADC
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist


# This module's spesification
# <rtc-template block="module_spec">
soilmoisture_sensor_spec = ["implementation_id", "Soilmoisture_Sensor", 
         "type_name",         "Soilmoisture_Sensor", 
         "description",       "Soil moisture sensor compornent", 
         "version",           "1.0.0", 
         "vendor",            "VenderName", 
         "category",          "Controller", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         ""]

class Soilmoisture_Sensor(OpenRTM_aist.DataFlowComponentBase):
	
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_soilmoisture = OpenRTM_aist.instantiateDataType(RTC.TimedFloat)
        """
        """
        self._soilmoistureOut = OpenRTM_aist.OutPort("soilmoisture", self._d_soilmoisture)


    def onInitialize(self):
		
        self.adc = ADC(address=0x08)
        self.channel = 2

        # Set OutPort buffers
        self.addOutPort("soilmoisture",self._soilmoistureOut)
		
        return RTC.RTC_OK
	

    def onExecute(self, ec_id):
        value = self.adc.read(self.channel)

        self._d_soilmoisture.data = float(value)
        OpenRTM_aist.setTimestamp(self._d_soilmoisture)

        print("soilmoisture:", self._d_soilmoisture.data)
        self._soilmoistureOut.write()
        
        return RTC.RTC_OK
	


def Soilmoisture_SensorInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=soilmoisture_sensor_spec)
    manager.registerFactory(profile,
                            Soilmoisture_Sensor,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    Soilmoisture_SensorInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("Soilmoisture_Sensor" + args)

def main():
    # remove --instance_name= option
    argv = [i for i in sys.argv if not "--instance_name=" in i]
    # Initialize manager
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()

if __name__ == "__main__":
    main()

