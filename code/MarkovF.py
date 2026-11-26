#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file Marcof.py
 @brief Marcof compornent
 @date $Date$


"""

import sys
import time
import numpy as np
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

# This module's spesification
# <rtc-template block="module_spec">
marcof_spec = ["implementation_id", "Marcof", 
         "type_name",         "Marcof", 
         "description",       "Marcof model compornent", 
         "version",           "1.0.0", 
         "vendor",            "VenderName", 
         "category",          "Controller", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         ""]

class Marcof(OpenRTM_aist.DataFlowComponentBase):

    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        # InPort
        self._d_trigger = OpenRTM_aist.instantiateDataType(RTC.TimedString)
        self._triggerIn = OpenRTM_aist.InPort("trigger", self._d_trigger)

        # OutPort
        self._d_emotion = OpenRTM_aist.instantiateDataType(RTC.TimedFloatSeq)
        self._emotionOut = OpenRTM_aist.OutPort("emotion", self._d_emotion)


    def onInitialize(self):
		
        # Set InPort buffers
        self.addInPort("trigger",self._triggerIn)

        # Set OutPort buffers
        self.addOutPort("emotion",self._emotionOut)

        self.now = np.array([0.25, 0.25, 0.25, 0.25], dtype=float)
        self.trigger = ""
		
        return RTC.RTC_OK
	
    def MarkovF(self, trigger):
        # 基本遷移行列
        # [Joy, Angry, Sad, Relax]
        Q = np.array([
            [0.7,    0,      0,      0.3],
            [0.0375, 0.6898,  0.2727, 0],
            [0,      0.3102,  0.6443, 0.0455],
            [0.2625, 0,      0.083,  0.6545]
        ])

        # triggerごとの感情への影響
        if trigger == "water":
            J = np.array([0.4, 1.6, 1.4, 0.6])
        elif trigger == "light":
            J = np.array([0.7, 1.0, 1.0, 1.3])
        elif trigger == "over water":
            J = np.array([1.5, 0.6, 0.5, 1.4])
        elif trigger == "dry":
            J = np.array([1.3, 0.5, 0.8, 1.4])
        elif trigger == "little dry":
            J = np.array([1.1, 0.8, 0.9, 1.2])
        elif trigger == "hamizu":
            J = np.array([0.6, 1.3, 1.4, 0.7])
        elif trigger == "dark":
            J = np.array([1.1, 1.1, 1.0, 0.8])
        elif trigger == "night":
            J = np.array([1.1, 1.2, 1.1, 0.6])
        elif trigger == "come":
            J = np.array([0.8, 1.0, 1.0, 1.2])
        elif trigger == "touch":
            J = np.array([0.8, 1.2, 1.1, 0.9])
        else:
            # 未知のtriggerの場合
            J = np.array([1.0, 1.0, 1.0, 1.0])

        # 遷移行列P
        P = np.zeros((4, 4), dtype=float)

        for i in range(4):
            for j in range(4):
                if i != j:
                    P[i, j] = (1.0 + J[j] - J[i]) * Q[i, j]

        # 各列の合計が1になるように自己遷移を設定
        for i in range(4):
            P[i, i] = 1.0 - np.sum(P[:, i])

        # 現在の感情状態から次の感情状態を計算
        Y = P @ self.now

        # 次回のために現在状態を更新
        self.now = Y.copy()

        return Y


    def onExecute(self, ec_id):

        if self._triggerIn.isNew():
            data = self._triggerIn.read()
            self.trigger = data.data
            print("received: ", self.trigger)
            if self.trigger == "night":
                emotion = np.array([-1.0, -1.0, -1.0, -1.0])
            else:
                emotion = self.MarkovF(self.trigger) #ここにマルコフ処理
            self._d_emotion.data = emotion.tolist()
            OpenRTM_aist.setTimestamp(self._d_emotion)
            self._emotionOut.write(self._d_emotion.data)
            print("emotion: ", self._d_emotion.data)
        else:
            print("no new data")
     
        return RTC.RTC_OK


def MarcofInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=marcof_spec)
    manager.registerFactory(profile,
                            Marcof,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    MarcofInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("Marcof" + args)

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

