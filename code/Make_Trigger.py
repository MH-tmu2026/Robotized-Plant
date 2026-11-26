#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file Make_trigger.py
 @brief Make_trigger compornent
 @date $Date$


"""

import sys
import time
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

# This module's spesification
# <rtc-template block="module_spec">
make_trigger_spec = ["implementation_id", "Make_trigger", 
         "type_name",         "Make_trigger", 
         "description",       "Control LED compornent", 
         "version",           "1.0.0", 
         "vendor",            "VenderName", 
         "category",          "Controller", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         ""]


class Make_trigger(OpenRTM_aist.DataFlowComponentBase):
#class Make_trigger(OpenRTM_aist.FlowComponentBase):

    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)
        #OpenRTM_aist.FlowComponentBase.__init__(self, manager)

        # Inport
        self._d_state = RTC.TimedFloatSeq(RTC.Time(0, 0), [])
        self._stateIn = OpenRTM_aist.InPort("state", self._d_state)

        # Outport
        self._d_trigger = OpenRTM_aist.instantiateDataType(RTC.TimedString)
        self._triggerOut = OpenRTM_aist.OutPort("trigger", self._d_trigger)


    def onInitialize(self):
		
        # Set InPort buffers
        self.addInPort("state",self._stateIn)

        # Set OutPort buffers
        self.addOutPort("trigger",self._triggerOut)


        self.soil_before = -1
        self.leaf_before = -1
        self.night_count = 0
        self.baseline_people = 1
		
        return RTC.RTC_OK
	

    def onExecute(self, ec_id):

        if self._stateIn.isNew():
            state = self._stateIn.read()
            data = state.data
            print("received: ", state.data)

            light = data[0]
            soil = data[1]
            leaf = data[2]
            touch = data[3]
            people = data[4]

            trigger = None
            if light < 150:
                trigger = "dark"
                self.night_count += 1
                if self.night_count >= 300:
                    trigger = "night"
            elif self.soil_before > 450 and (self.soil_before - soil) > 50:
                trigger = "water"
            elif self.soil_before < 400 and (self.soil_before - soil) > 50:
                trigger = "over water"
            elif self.leaf_before > 450 and (self.leaf_before - leaf) > 150:
                trigger = "leaf"
                today_leaf = True
            elif touch == 1:
                trigger = "touch"
            elif people > self.baseline_people + 0.5:
                trigger = "come"
            elif soil > 500:
                trigger = "dry"
            elif soil > 450:
                trigger = "little dry"
            
            if trigger != "dark":
                self.night_count = 0
            
            self._d_trigger.data = trigger
            OpenRTM_aist.setTimestamp(self._d_trigger)
            self._triggerOut.write()

            self.soil_before = soil
            self.leaf_before = leaf
            
        else:
            print("no new data")
     
        return RTC.RTC_OK



def Make_triggerInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=make_trigger_spec)
    manager.registerFactory(profile,
                            Make_trigger,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    Make_triggerInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("Make_trigger" + args)

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

