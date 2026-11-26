#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file Camera.py
 @brief Camera component for person detection
"""

import sys
import time
sys.path.append(".")
import depthai as dai
import blobconverter
#import cv2

# Import RTM module
import RTC
import OpenRTM_aist

# This module's spesification
# <rtc-template block="module_spec">
camera_spec = [
    "implementation_id", "Camera",
    "type_name",         "Camera",
    "description",       "Camera component",
    "version",           "1.0.0",
    "vendor",            "VenderName",
    "category",          "Controller",
    "activity_type",     "PERIODIC",
    "max_instance",      "1",
    "language",           "Python",
    "lang_type",          "SCRIPT",
    ""
]

# DepthAI pipeline
def create_pipeline():
    pipeline = dai.Pipeline()

    cam = pipeline.create(dai.node.ColorCamera)
    cam.setPreviewSize(544, 320)
    cam.setInterleaved(False)
    cam.setBoardSocket(dai.CameraBoardSocket.CAM_A)

    detection_nn = pipeline.create(dai.node.MobileNetDetectionNetwork)
    detection_nn.setBlobPath(blobconverter.from_zoo(name="person-detection-retail-0013",shaves=7))
    detection_nn.setConfidenceThreshold(0.5)
    cam.preview.link(detection_nn.input)

    #xout_rgb = pipeline.create(dai.node.XLinkOut)
    #xout_rgb.setStreamName("rgb")
    #cam.preview.link(xout_rgb.input)
    
    xout_nn = pipeline.create(dai.node.XLinkOut)
    xout_nn.setStreamName("detections")
    detection_nn.out.link(xout_nn.input)

    return pipeline


# Camera RTC
class Camera(OpenRTM_aist.DataFlowComponentBase):

    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        # OutPort
        self._d_people = OpenRTM_aist.instantiateDataType(RTC.TimedFloat)
        self._peopleOut = OpenRTM_aist.OutPort("people", self._d_people)

        # DepthAI関連
        self.pipeline = None
        self.device = None
        self.q_det = None


    def onInitialize(self):

        self.addOutPort("people", self._peopleOut)

        return RTC.RTC_OK


    def onActivated(self, ec_id):
        print("DepthAI 人物検出システム開始！ Ctrl+Cで終了します。")

        try:
            self.pipeline = create_pipeline()
            self.device = dai.Device(self.pipeline)
            #self.q_rgb = self.device.getOutputQueue(name="rgb", maxSize=1, blocking=False)
            self.q_det = self.device.getOutputQueue(name="detections", maxSize=1, blocking=False)

        except Exception as e:
            print(f"camera RTC: 起動エラー: {e}")
            return RTC.RTC_ERROR

        return RTC.RTC_OK


    def onExecute(self, ec_id):

        if self.q_det is None:
            return RTC.RTC_OK

        try:
            in_det = self.q_det.get()
            dets = in_det.detections

            #for det in dets:
            #    xmin = int(det.xmin * frame.shape[1])
            #    ymin = int(det.ymin * frame.shape[0])
            #    xmax = int(det.xmax * frame.shape[1])
            #    ymax = int(det.ymax * frame.shape[0])
            #    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)

            people_count = len(dets)
            self._d_people.data = float(people_count)
            OpenRTM_aist.setTimestamp(self._d_people)
            self._peopleOut.write()

            print("people:", people_count)

        except Exception as e:
            print(f"Camera RTC: 実行エラー: {e}")

        return RTC.RTC_OK


    def close_camera(self):

        self.q_det = None

        if self.device is not None:
            try:
                self.device.close()
                print("カメラとの接続を終了しました。")

            except Exception as e:
                print(f"Camera RTC: 終了処理エラー: {e}")
                
        self.device = None
        self.pipeline = None


    def onDeactivated(self, ec_id):

        self.close_camera()
        #print("終了しました。")
        #cv2.destroyAllWindows()

        return RTC.RTC_OK


def CameraInit(manager):
    profile = OpenRTM_aist.Properties(
        defaults_str=camera_spec
    )

    manager.registerFactory(
        profile,
        Camera,
        OpenRTM_aist.Delete
    )


def MyModuleInit(manager):
    CameraInit(manager)

    instance_name = [
        i for i in sys.argv
        if "--instance_name=" in i
    ]

    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""

    manager.createComponent("Camera" + args)


def main():
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()


if __name__ == "__main__":
    main()
