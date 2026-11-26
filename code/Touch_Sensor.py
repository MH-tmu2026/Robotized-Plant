#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file Touch_Sensor.py
 @brief Touch sensor compornent
 @date $Date$


"""

import sys
import time
import RPi.GPIO as GPIO
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist


# This module's spesification
# <rtc-template block="module_spec">
touch_sensor_spec = ["implementation_id", "Touch_Sensor", 
         "type_name",         "Touch_Sensor", 
         "description",       "Touch sensor compornent", 
         "version",           "1.0.0", 
         "vendor",            "VenderName", 
         "category",          "Controller", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         ""]

class Touch_Sensor(OpenRTM_aist.DataFlowComponentBase):
	
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_touch = OpenRTM_aist.instantiateDataType(RTC.TimedFloat)
        """
        """
        self._touchOut = OpenRTM_aist.OutPort("touch", self._d_touch)


    def onInitialize(self):		
        
        self.TOUCH_PIN = 17
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TOUCH_PIN, GPIO.IN)

        # Set OutPort buffers
        self.addOutPort("touch",self._touchOut)
		
        return RTC.RTC_OK
	

    def onExecute(self, ec_id):

        value = GPIO.input(self.TOUCH_PIN)

        self._d_touch.data = float(value)
        OpenRTM_aist.setTimestamp(self._d_touch)

        print("touch:", self._d_touch.data)
        self._touchOut.write()
        
        return RTC.RTC_OK



def Touch_SensorInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=touch_sensor_spec)
    manager.registerFactory(profile,
                            Touch_Sensor,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    Touch_SensorInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("Touch_Sensor" + args)

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

