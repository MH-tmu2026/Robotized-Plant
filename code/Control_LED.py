#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file Control_LED.py
 @brief control LED compornent
 @date $Date$


"""

import sys
import time
import numpy as np
from rpi_ws281x import PixelStrip, Color
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist


# This module's spesification
# <rtc-template block="module_spec">
control_led_spec = ["implementation_id", "Control_LED", 
         "type_name",         "Control_LED", 
         "description",       "Control LED compornent", 
         "version",           "1.0.0", 
         "vendor",            "VenderName", 
         "category",          "Controller", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         ""]


class Control_LED(OpenRTM_aist.DataFlowComponentBase):

    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_emotion = OpenRTM_aist.instantiateDataType(RTC.TimedFloatSeq)
        """
        """
        self._emotionIn = OpenRTM_aist.InPort("emotion", self._d_emotion)


    def onInitialize(self):
		
        # Set InPort buffers
        self.addInPort("emotion",self._emotionIn)
		
        # LED strip configuration
        LED_COUNT = 30
        LED_PIN = 18
        LED_FREQ_HZ = 800000
        LED_DMA = 10
        LED_BRIGHTNESS = 255
        LED_INVERT = False
        LED_CHANNEL = 0

        # 初期化
        self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                        LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()
        
        self.last_color = [0, 0, 0]
		
        return RTC.RTC_OK
	

    def onDeactivated(self, ec_id):
		
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()

        return RTC.RTC_OK


    def close_second(self, Y):
        m = max(Y) # 最大値
        max_index = np.argmax(Y)
        array_filtered = [x for i, x in enumerate(Y) if i != max_index] # 最大値を除外
        second_value = max(array_filtered) #二番手の値
        second_index = [i for i, x in enumerate(Y) if x == second_value][0] # 元の配列でのインデックス
        delta = m - second_value #最大値との差
        isclose = delta < 0.05
        return second_value, second_index, isclose

    #
    def emotion_to_color(self, emotion):

        Jlight = [237, 219, 91]      # Joy
        Alight = [220, 9, 8]         # Angry
        Slight = [20, 91, 208]       # Sad
        Rlight = [107, 219, 130]     # Relax

        lights = [
            Jlight,
            Alight,
            Slight,
            Rlight]

        if emotion[0] == -1:
            color = Color(0, 0, 0)
            return color

        max_emotion_value = max(emotion) 
        max_emotion = np.argmax(emotion)  # 最大感情のインデックス
        second_value, second, isclose = self.close_second(emotion) # 二番手の感情

        if isclose:
            # 最大と二番手の感情が拮抗している場合 → ブレンド
            w1 = max_emotion_value / (max_emotion_value + second_value)
            w2 = second_value / (max_emotion_value + second_value)
            r = int(lights[max_emotion][0] * w1 + lights[second][0] * w2)
            g = int(lights[max_emotion][1] * w1 + lights[second][1] * w2)
            b = int(lights[max_emotion][2] * w1 + lights[second][2] * w2)
        else:
            # 最大感情だけを反映
            r, g, b = lights[max_emotion]
        
        color = Color(r, g, b)

        return color


    def set_color(self, color):
        print("set_color")
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            time.sleep(0.5)
        self.strip.show()


    def onExecute(self, ec_id):
        if self._emotionIn.isNew():
            data = self._emotionIn.read()
            emotion = data.data
            color = self.emotion_to_color(emotion)
            if color != self.last_color:
                self.set_color(color)
                self.last_color = color
        else:
            print("no new data")
     
        return RTC.RTC_OK



def Control_LEDInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=control_led_spec)
    manager.registerFactory(profile,
                            Control_LED,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    Control_LEDInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("Control_LED" + args)

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

