#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file Memory_State.py
 @brief Memory state comportnent
 @date $Date$


"""

import sys
import time
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

#Sensors
SENSOR_IDS = [
    "light",
    "soil",
    "leaf",
    "touch",
    "people"
]

# This module's spesification
# <rtc-template block="module_spec">
memory_state_spec = ["implementation_id", "Memory_State", 
         "type_name",         "Memory_State", 
         "description",       "Memory state comportnent", 
         "version",           "1.0.0", 
         "vendor",            "VenderName", 
         "category",          "Controller", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         ""]


class Memory_State(OpenRTM_aist.DataFlowComponentBase):

    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        # each sensor's InPort
        self._sensor_ports = {}

        # each sensor's object
        self._sensor_data = {}

        # OutPort
        self._d_state = RTC.TimedFloatSeq(RTC.Time(0, 0), [])
        self._stateOut = OpenRTM_aist.OutPort("state",self._d_state)


    def onInitialize(self):
		
        # Set InPort buffers
        for sensor_id in SENSOR_IDS:
            data = RTC.TimedFloat(RTC.Time(0, 0), 0.0)
            port = OpenRTM_aist.InPort(sensor_id, data)
            self.addInPort(sensor_id, port)
            self._sensor_ports[sensor_id] = port
            self._sensor_data[sensor_id] = data
		
        # Set OutPort buffers
        self.addOutPort("state",self._stateOut)
        return RTC.RTC_OK
	

    #def onActivated(self, ec_id):
    
    #    print("Memory_State activated.")

    #    return RTC.RTC_OK
	

    def onExecute(self, ec_id):
        state = []
        # [light, soil, leaf, touch, people]

        for sensor_id, port in self._sensor_ports.items():
            if port.isNew():
                self._sensor_data[sensor_id] = port.read()
            value = self._sensor_data[sensor_id].data
            state.append(value)
            print(f"{sensor_id}: {value}")
            
        self._d_state.data = state
        self._stateOut.write()

        return RTC.RTC_OK



def Memory_StateInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=memory_state_spec)
    manager.registerFactory(profile,
                            Memory_State,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    Memory_StateInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("Memory_State" + args)

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

