#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file Light_Sensor.py
 @brief Light sensor compornent
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
light_sensor_spec = ["implementation_id", "Light_Sensor", 
         "type_name",         "Light_Sensor", 
         "description",       "Light sensor compornent", 
         "version",           "1.0.0", 
         "vendor",            "VenderName", 
         "category",          "Controller", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         ""]


class Light_Sensor(OpenRTM_aist.DataFlowComponentBase):
	
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_light = OpenRTM_aist.instantiateDataType(RTC.TimedFloat)
        """
        """
        self._lightOut = OpenRTM_aist.OutPort("light", self._d_light)


    def onInitialize(self):

        self.adc = ADC(address=0x08)
        self.channel = 4

        # Set OutPort buffers
        self.addOutPort("light",self._lightOut)
		
        return RTC.RTC_OK
	

    def onExecute(self, ec_id):
        value = self.adc.read(self.channel)

        self._d_light.data = float(value)
        OpenRTM_aist.setTimestamp(self._d_light)

        print("light:", self._d_light.data)
        self._lightOut.write()
        
        return RTC.RTC_OK



def Light_SensorInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=light_sensor_spec)
    manager.registerFactory(profile,
                            Light_Sensor,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    Light_SensorInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("Light_Sensor" + args)

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

