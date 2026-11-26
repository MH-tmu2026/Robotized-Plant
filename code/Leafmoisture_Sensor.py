#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file Leafmoisture_Sensor.py
 @brief Leafmoisture sensor compornent
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
leafmoisture_sensor_spec = ["implementation_id", "Leafmoisture_Sensor", 
         "type_name",         "Leafmoisture_Sensor", 
         "description",       "Leafmoisture sensor compornent", 
         "version",           "1.0.0", 
         "vendor",            "VenderName", 
         "category",          "Controller", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         ""]


class Leafmoisture_Sensor(OpenRTM_aist.DataFlowComponentBase):
	
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_leafmoisture = OpenRTM_aist.instantiateDataType(RTC.TimedFloat)
        """
        """
        self._leafmoistureOut = OpenRTM_aist.OutPort("leafmoisture", self._d_leafmoisture)


    def onInitialize(self):
        self.adc = ADC(address=0x08)
        self.channel = 0

        # Set OutPort buffers
        self.addOutPort("leafmoisture",self._leafmoistureOut)
		
        return RTC.RTC_OK
	

    def onExecute(self, ec_id):
        value = self.adc.read(self.channel)

        self._d_leafmoisture.data = float(value)
        OpenRTM_aist.setTimestamp(self._d_leafmoisture)

        print("leafmoisture:", self._d_leafmoisture.data)
        self._leafmoistureOut.write()
        
        return RTC.RTC_OK


def Leafmoisture_SensorInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=leafmoisture_sensor_spec)
    manager.registerFactory(profile,
                            Leafmoisture_Sensor,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    Leafmoisture_SensorInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("Leafmoisture_Sensor" + args)

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

