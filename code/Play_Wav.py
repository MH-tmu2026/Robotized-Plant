#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file Play_Wav.py
 @brief Play wav file comportnent
 @date $Date$


"""

import sys
import time
import numpy as np
from os import environ
import pygame.mixer
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist


# This module's spesification
# <rtc-template block="module_spec">
play_wav_spec = ["implementation_id", "Play_Wav", 
         "type_name",         "Play_Wav", 
         "description",       "Make state comportnent", 
         "version",           "1.0.0", 
         "vendor",            "VenderName", 
         "category",          "Controller", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         ""]


class Play_Wav(OpenRTM_aist.DataFlowComponentBase):

    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_emotion = OpenRTM_aist.instantiateDataType(RTC.TimedFloatSeq)
        """
        """
        self._emotionIn = OpenRTM_aist.InPort("emotion", self._d_emotion)

        self._d_action = OpenRTM_aist.instantiateDataType(RTC.TimedLong)
        """
        """
        self._actionIn = OpenRTM_aist.InPort("action", self._d_action)

        self._d_trigger = OpenRTM_aist.instantiateDataType(RTC.TimedString)
        """
        """
        self._triggerIn = OpenRTM_aist.InPort("trigger", self._d_trigger)

        self._d_speech_event = OpenRTM_aist.instantiateDataType(RTC.TimedLong)
        """
        """
        self._speech_eventOut = OpenRTM_aist.OutPort("speech_event", self._d_speech_event)


    def onInitialize(self):

        # Set InPort buffers
        self.addInPort("emotion", self._emotionIn)
        self.addInPort("action", self._actionIn)
        self.addInPort("trigger", self._triggerIn)

        # Set OutPort buffers
        self.addOutPort("speech_event", self._speech_eventOut)

        self.emotion = []
        self.trigger = ""

        return RTC.RTC_OK
	
    #
    #def onActivated(self, ec_id):

    #    return RTC.RTC_OK

    def emotion_to_string(self, emotion):
        emotion_string = [
            "joy",
            "angry",
            "sad",
            "relax"]

        if emotion[0] == -1:
            voice = "NONE"
            return voice

        #max_emotion_value = max(emotion) 
        max_emotion = np.argmax(emotion)  # 最大感情のインデックス

        voice = emotion_string[max_emotion]
        
        return voice


    def Playwav(self, emo, tri):
        if tri == "hamizu" and tri == "water":
            tri = "ありがとう"
        elif tri == "come":
            tri = "葉水"
        elif tri  == "dry":
            tri = "水"
        else:
            tri = ""
        
        sound = 'voice/' + tri  + emo +'.wav'
        pygame.mixer.init()
        wav_sound = pygame.mixer.Sound(sound)
        wav_sound.play()

        while pygame.mixer.get_busy():
            pass


    def onExecute(self, ec_id):

        if self._emotionIn.isNew():
            self._d_emotion = self._emotionIn.read()
            self.emotion = self._d_emotion.data

        if self._triggerIn.isNew():
            self._d_trigger = self._triggerIn.read()
            self.trigger = self._d_trigger.data

        if self._actionIn.isNew():
            self._d_action = self._actionIn.read()
            action = self._d_action.data
            if action == 1:
                self._d_speech_event.data = 1
                OpenRTM_aist.setTimestamp(self._d_speech_event)
                self._speech_eventOut.write()
                self.Playwav(self.emotion_to_string(self.emotion), self.trigger)
                #self.Playwav('angry','come')
                self._d_speech_event.data = 0

        return RTC.RTC_OK



def Play_WavInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=play_wav_spec)
    manager.registerFactory(profile,
                            Play_Wav,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    Play_WavInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("Play_Wav" + args)

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

