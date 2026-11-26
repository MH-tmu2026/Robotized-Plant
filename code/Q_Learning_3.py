#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file Q_Learning.py
 @brief Q Learning component
 @date $Date$
"""

import sys
import time
import os
import numpy as np
from collections import defaultdict
import csv
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist


# This module's specification
# <rtc-template block="module_spec">
q_learning_spec = [
    "implementation_id", "Q_Learning",
    "type_name",         "Q_Learning",
    "description",       "Q Learning component",
    "version",           "1.0.0",
    "vendor",            "VenderName",
    "category",          "Controller",
    "activity_type",     "STATIC",
    "max_instance",      "1",
    "language",          "Python",
    "lang_type",         "SCRIPT",
    ""
]



# Q学習エージェント
class QAgent:
    def __init__(self, actions):
        self.q_table = defaultdict(lambda: np.zeros(len(actions)))
        # 各状態の訪問（学習）回数
        self.visit_counts = defaultdict(int)
        self.actions = actions
        self.alpha = 0.1
        self.gamma = 0.95
        self.epsilon = 0.9
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.99

    def choose_action(self, state):
        # ε-greedy
        if np.random.uniform(0, 1) < self.epsilon:
            return int(np.random.choice(self.actions))
        else:
            self.check_state_exist(state)
            return int(np.argmax(self.q_table[state]))

    def learn(self, state, action, reward, next_state):
        self.check_state_exist(next_state)
        q_predict = self.q_table[state][action]
        q_target = (reward + self.gamma * np.max(self.q_table[next_state]))
        self.q_table[state][action] += self.alpha * (q_target - q_predict)
        # この状態で学習が行われた回数をカウントアップ
        self.visit_counts[state] += 1

    def check_state_exist(self, state):
        if state not in self.q_table:
            self.q_table[state] = np.zeros(len(self.actions))

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    #q_table保存用関数を用意する？


# Q_Learning RTC
class Q_Learning(OpenRTM_aist.DataFlowComponentBase):

    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self,manager)

        self._d_state = RTC.TimedFloatSeq(RTC.Time(0, 0),[])
        self._stateIn = OpenRTM_aist.InPort("state",self._d_state)

        self._d_speech_event = RTC.TimedLong(RTC.Time(0, 0),0)
        self._speechEventIn = OpenRTM_aist.InPort("speech_event",self._d_speech_event)

        self._d_action = RTC.TimedLong(RTC.Time(0, 0),0)
        self._actionOut = OpenRTM_aist.OutPort("action",self._d_action)

    def onInitialize(self):

        # InPort
        self.addInPort("state",self._stateIn)
        self.addInPort("speech_event",self._speechEventIn)

        # OutPort
        self.addOutPort("action",self._actionOut)

        # Q Agent
        self.agent = QAgent(actions=[0, 1])


        # 学習制御用の変数
        self.last_speech_time = None
        self.soil_moisture_at_speech = None
        self.leaf_moisture_at_speech = None
        self.wait_for_reward = False
        self.MAX_WAIT_SEC = 90
        self.total_reward = 0

        #通常時学習用
        self.prev_state = None
        self.prev_action = None

        # 保留変数
        self.pending_state = None
        self.pending_action = None
        self.waiting_for_speech = False
        
        self.SPEECH_EVENT_TIMEOUT_SEC = 10.0
        self.speech_request_time = None

        self.last_action = None
        self.last_action_state = None
        self.last_action_soil = None
        self.last_action_leaf = None

        self.latest_state = None
        self.latest_light = None
        self.latest_soil = None
        self.latest_leaf = None
        self.latest_touch = None
        self.latest_people = None


        # CSV保存先
        self.log_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "q_learning_log.csv"
        )

        # Qテーブル保存先
        self.q_table_log_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "q_table_log.csv"
        )

        return RTC.RTC_OK


    def onActivated(self, ec_id):

        self.start_time = time.time()

        # CSVファイルを初期化
        with open(self.log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "elapsed_time",
                "SoilMoisture", 
                "LeafMoisture", 
                "PeopleCount", 
                "reward",
                "total_reward"
            ])

        # QテーブルCSVを初期化
        with open(self.q_table_log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "elapsed_time",
                "state",
                "q_0",
                "q_1",
                "epsilon",
                "total_reward"
            ])

        print("Q_Learning activated.")
        print("Log file:", self.log_file)
        print("Q-table log file:", self.q_table_log_file)

        return RTC.RTC_OK

    def save_q_table(self):
        elapsed_time = time.time() - self.start_time

        with open(self.q_table_log_file,"a",newline="") as f:
            writer = csv.writer(f)

            for state, q_values in self.agent.q_table.items():
                writer.writerow([
                    elapsed_time,
                    state,
                    q_values[0],
                    q_values[1],
                    self.agent.epsilon,
                    self.total_reward
                ])

    def onExecute(self, ec_id):
        # 新しいセンサ状態を受信
        state_updated = False

        if self._stateIn.isNew():
            self._d_state = self._stateIn.read()
            data = self._d_state.data
            print("received:", data)

            if len(data) < 5:
                print("Error: state data length is less than 5.")
                return RTC.RTC_OK

            light = data[0]
            soil = data[1]
            leaf = data[2]
            touch = data[3]
            people = data[4]

            # 最新値を保存
            self.latest_light = light
            self.latest_soil = soil
            self.latest_leaf = leaf
            self.latest_touch = touch
            self.latest_people = people

            # 状態の離散化
            soil_disc = (soil // 50) * 50
            leaf_disc = ((leaf // 200) * 200)

            # 人数を0,1,2,3以上に丸める
            if people == 0:
                people_cat = 0
            elif people == 1:
                people_cat = 1
            elif people == 2:
                people_cat = 2
            else:
                people_cat = 3

            # 学習用の状態
            state = (soil_disc, leaf_disc, people_cat)

            self.latest_state = state
            state_updated = True


        # speech_eventを受信
        speech_started = False
        if self._speechEventIn.isNew():
            self._d_speech_event = self._speechEventIn.read()
            speech_event = self._d_speech_event.data
            print(
                "speech_event:", speech_event,
                "last_action:", self.last_action,
                "last_action_state:", self.last_action_state,
                "wait_for_reward:", self.wait_for_reward
            )
            # 1 = 実際に発話した
            if speech_event == 1:
                # すでに報酬待ちなら無視
                if self.wait_for_reward:
                    print(
                        "Warning: speech_event received "
                        "while waiting for reward."
                    )
                elif not self.waiting_for_speech:
                    print(
                        "Warning: speech_event received "
                        "without previous action=1."
                    )
                elif self.last_action_state is None:
                    print(
                        "Warning: no stored action state."
                    )
                else:

                    # 実際に発話した瞬間の状態を確定
                    self.pending_state = self.last_action_state
                    self.pending_action = 1

                    self.soil_moisture_at_speech = self.latest_soil
                    self.leaf_moisture_at_speech = self.latest_leaf
                    self.last_speech_time = time.time()

                    self.wait_for_reward = True
                    self.waiting_for_speech = False

                    self.speech_request_time = None

                    speech_started = True

                    # 通常学習をいったんクリア
                    self.prev_state = None
                    self.prev_action = None


                    print(">>> 発話を検知。報酬待ちモードへ移行")
            

        # 発話開始通知のタイムアウト確認
        # speech_eventの有無にかかわらず毎周期確認

        # 発話開始通知のタイムアウト確認
        if self.waiting_for_speech and self.speech_request_time is not None:
            elapsed = time.time() - self.speech_request_time

            if elapsed >= self.SPEECH_EVENT_TIMEOUT_SEC:
                print("発話開始通知がタイムアウトしました")

                self.waiting_for_speech = False
                self.speech_request_time = None
                self.wait_for_reward = False

                self.prev_state = None
                self.prev_action = None

                self.pending_state = None
                self.pending_action = None
                self.last_speech_time = None

                self.soil_moisture_at_speech = None
                self.leaf_moisture_at_speech = None

                self.last_action = None
                self.last_action_state = None
                self.last_action_soil = None
                self.last_action_leaf = None

                return RTC.RTC_OK

        if self.waiting_for_speech:
            return RTC.RTC_OK

        if speech_started:
            return RTC.RTC_OK


        # 報酬待ちモード
        if self.wait_for_reward:
            current_time = time.time()
            state = self.latest_state

            reward = 0
            done_waiting = False

            # 時間切れ
            if (self.last_speech_time is not None and current_time - self.last_speech_time > self.MAX_WAIT_SEC):
                reward = -1
                done_waiting = True
                print(">>> 報酬なし: 時間切れ...")

            # センサ値が更新された場合
            elif state_updated:
                soil = self.latest_soil
                leaf = self.latest_leaf
                touch = self.latest_touch
                state = self.latest_state

                delta_soil = (self.soil_moisture_at_speech - soil)

                delta_leaf = (self.leaf_moisture_at_speech - leaf)

                if delta_soil > 50:
                    reward = 100
                    done_waiting = True
                    print(">>> 報酬獲得: 水やりされました！")

                elif delta_leaf > 100:
                    reward = 50
                    done_waiting = True
                    print(">>> 報酬獲得: 葉水されました！")

                elif touch:
                    reward = 10
                    done_waiting = True
                    print(">>> 報酬獲得: タッチされました！")


            # 報酬確定後に学習

            if done_waiting:
                if self.pending_state is not None:
                    self.agent.learn(self.pending_state, self.pending_action, reward, state)
                    self.save_q_table()

                self.total_reward += reward

                print(
                    "reward:", reward,
                    "total_reward:", self.total_reward
                )

                elapsed_time = time.time() - self.start_time

                with open(self.log_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        elapsed_time,
                        self.latest_soil,
                        self.latest_leaf,
                        self.latest_people,
                        reward,
                        self.total_reward
                    ])


                # リセット
                self.wait_for_reward = False
                self.pending_state = None
                self.pending_action = None
                self.last_speech_time = None
                self.soil_moisture_at_speech = None
                self.leaf_moisture_at_speech = None
                self.last_action = None
                self.last_action_state = None
                self.last_action_soil = None
                self.last_action_leaf = None

            return RTC.RTC_OK


        # 通常モード
        if not state_updated:
            return RTC.RTC_OK

        state = self.latest_state
        soil = self.latest_soil

        # 行動選択
        action = self.agent.choose_action(state)


        # 即時報酬
        reward = 0
        if action == 1:
            if soil < 400:
                reward = -2

        self.total_reward += reward

        # 累積報酬を記録
        if reward != 0:
            elapsed_time = time.time() - self.start_time

            with open(self.log_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    elapsed_time,
                    self.latest_soil,
                    self.latest_leaf,
                    self.latest_people,
                    reward,
                    self.total_reward
                ])


        # 前回状態を学習
        if (self.prev_state is not None and self.prev_action is not None):
            self.agent.learn(self.prev_state, self.prev_action, reward, state)
            self.save_q_table()

        # actionを出力
        self._d_action.data = int(action)
        OpenRTM_aist.setTimestamp(self._d_action)
        self._actionOut.write()

        print("action:",action)


        # action=1だった場合
        if action == 1:
            self.waiting_for_speech = True
            self.speech_request_time = time.time()   

            # 実際の発話に対応する候補状態を保存
            self.last_action = 1
            self.last_action_state = state
            self.last_action_soil = soil
            self.last_action_leaf = self.latest_leaf

            self.prev_state = None
            self.prev_action = None


        else:
            # action=0の場合は通常学習
            self.prev_state = state
            self.prev_action = action

            self.agent.decay_epsilon()

        return RTC.RTC_OK



def Q_LearningInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=q_learning_spec)
    manager.registerFactory(profile, 
                            Q_Learning,
                            OpenRTM_aist.Delete)


def MyModuleInit(manager):
    Q_LearningInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""

    # Create component
    comp = manager.createComponent("Q_Learning" + args)

def main():
    # remove --instance_name= option
    argv = [i for i in sys.argv if "--instance_name=" not in i]
    # Initialize manager
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()

if __name__ == "__main__":
    main()