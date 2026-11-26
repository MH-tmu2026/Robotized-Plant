# Robotized-Plant

## 概要
Robotized-Plantは、植物とペットロボットを融合させたコミュニケーションシステムです。

植物にセンサを取り付け、周囲の環境状態や世話行為を検知します。発声やLEDライトの色の変化でユーザにインタラクトします。
また、学習機構を取り入れており、置かれた環境に適応して発声のタイミングをコントロールします。

従来のペットロボットと異なり植物が主体であるため、世話が必要であり、また視覚的に成長を体験することができます。
アレルギーや施設の規則などの事情で動物のペットを飼うことのできない人に対し、類似の体験を提供することが期待できます。

OpenRTMで実装することにより、高い拡張性と、アップデートへの対応のしやすさを担保しています。

## 構成
Robotized-Plantは主にセンサコンポーネント群、内部処理コンポーネント群、出力コンポーネント群から構成されます。

センサコンポーネント群で植物の周辺状態を取得し、内部処理コンポーネント群へと送ります。
現在のRobotized-Plantでは、光センサコンポーネント、土壌水分センサコンポーネント、葉水センサコンポーネント、タッチセンサコンポーネント、カメラコンポーネントが実装されています。

内部処理コンポーネント群では、センサコンポーネント群から受け取ったセンサ値を内部状態を保持します。また、内部状態から植物の感情を決定したり、発声の有無を決定します。
現在のRobotized-Plantでは、内部状態記録コンポーネント、トリガー生成コンポーネント、感情決定コンポーネント、行動生成コンポーネントが実装されています。
また、感情決定にはマルコフ情動モデルを、行動生成にはQ-Learningを採用しており、これを任意の他アルゴリズムに変えることもできます。

出力コンポーネント群では、内部処理コンポーネント群から出力された結果を受けて外部へのインタラクトを行います。
現在のRobotized-Plantでは、音声再生コンポーネント、LED操作コンポーネントが実装されています。
音声再生コンポーネントでは感情を伴った非言語的な発声を行います。また、LEDはそのときの植物の感情に合わせて色を変化させます。

## 実装されている各コンポーネントの説明
現在Robotized-Plantシステムに実装されている各コンポーネントの説明です。

### 光センサコンポーネント
InPort：なし  
OutPort：light（TimedFloat型）  

光センサコンポーネントLight\_Sensor.pyはセンサコンポーネント群に属します。OutPortのlightは光量センサから取得した光量の値であり、内部状態記録コンポーネントMemory\_State.pyに送られます。

### 土壌水分センサコンポーネント
InPort：なし  
OutPort：soilmoisture（TimedFloat型）  

土壌水分センサコンポーネントSoilmoisture\_Sensor.pyはセンサコンポーネント群に属します。OutPortのsoilmoistureは土壌水分センサから取得した土壌水分量の値であり、内部状態記録コンポーネントMemory\_State.pyに送られます。

### 葉水センサコンポーネント
InPort：なし  
OutPort：leafmoisture（TimedFloat型）  

葉水センサコンポーネントLeafmoisture\_Sensor.pyはセンサコンポーネント群に属します。OutPortのleafmoistureは水滴センサから取得した水滴量の値であり、内部状態記録コンポーネントMemory\_State.pyに送られます。

### タッチセンサコンポーネント
InPort：なし  
OutPort：touch（TimedFloat型）  

タッチセンサコンポーネントTouch\_Sensor.pyはセンサコンポーネント群に属します。OutPortのtouchはタッチセンサから取得した値であり、内部状態記録コンポーネントMemory\_State.pyに送られます。

### カメラコンポーネント
InPort：なし  
OutPort：people（TimedFloat型）  

カメラコンポーネントCamera.pyはセンサコンポーネント群に属します。OutPortのpeopleはカメラ情報から取得・推定した周辺人物の人数であり、内部状態記録コンポーネントMemory\_State.pyに送られます。

### 内部状態記録コンポーネント
InPort：light（TimedFloat型）、soilmoisture（TimedFloat型）、leafmoisture（TimedFloat型）、touch（TimedFloat型）、people（TimedFloat型）  
OutPort：state（TimedFloatSeq型）  

内部状態記録コンポーネントMemory\_State.pyは内部処理コンポーネント群に属します。OutPortのstateは取得したデータをリスト状にまとめたものであり、トリガー生成コンポーネントMake\_Trigger.py、行動決定コンポーネントQ\_Learning.py、表示コンポーネントDisplay\_Now.pyに送られます。
起動時に生成するInPortの数を容易に変更できるような構造になっており、センサコンポーネントが増えた際に対応しやすいです。

### トリガー生成コンポーネント
InPort：state（TimedFloatSeq型）  
OutPort：trigger（TimedString型）  

トリガー生成コンポーネントMake\_Trigger.pyは内部処理コンポーネント群に属します。OutPortのtriggerは数秒間の間に発生した水分量や周辺人数の変化を示す識別文字列であり、感情決定コンポーネントMarkovF.py、音声再生コンポーネントPlay\_Wav.pyに送られます。

### 感情決定コンポーネント
InPort：trigger（TimedString型）  
OutPort：emotion（TimedFloatSeq型）  

感情決定コンポーネントMarkovF.pyは内部処理コンポーネント群に属します。OutPortのemotionは[joy, angry, sad, relax]のリストから表される植物の感情であり、音声再生コンポーネントPlay\_Wav.py、LED操作コンポーネントControl\_LED.pyに送られます。
現在、感情決定の方法にはマルコフ情動モデルとラッセルの感情円環モデルが用いています。
また、感情決定とは別に光量の値が一定の閾値を下回ったときは夜間モードに入り、これに影響を受ける出力コンポーネント群が動作しないようになります。これには、ユーザが行動していない時間にRobotized Plantが動作することによるユーザへの負担を避ける狙いがあります。

### 行動決定コンポーネント
InPort：state（TimedFloatSeq型）、speech\_event（TimedLong型）  
OutPort：action（TimedLong型）  

行動決定コンポーネントQ\_Learning.pyは内部処理コンポーネント群に属します。OutPortのactionは行動を起こす(1)か起こさない(0)かの二値であり、音声再生コンポーネントPlay\_Wav.pyに送られます。また、常時実行のサイクルが回る度にその時の累積報酬を取得し、csvファイルに出力します。
現在、行動決定にはQ学習を用いています。

### 音声再生コンポーネント
InPort：trigger（TimedString型）、emotion（TimedFloatSeq型）  
OutPort：speech\_event（TimedLong型） 

音声再生コンポーネントPlay\_Wav.pyは出力コンポーネント群に属します。OutPortのspeech\_eventは本コンポーネントが発声動作を実行したことを伝える二値の値で、行動決定コンポーネントQ\_Learning.pyに差し戻されます。これは、本コンポーネントは夜間モード時の間にも発声をしたとして学習が進まないようにするための措置です。
外部の状況や学習の結果を受け、直近に推定された感情に基づいた声色で発生をおこないます。また、夜間は発声を行いません。

### LED操作コンポーネント
InPort: emotion（TimedFloatSeq型）  
OutPort: なし  

LED操作コンポーネントControl\_LED.pyは出力コンポーネント群に属します。入力されたemotionに対応する色に点灯します。joy, angry, sad, relaxの4つの感情の内複数が拮抗する場合、色のブレンドが行われる。また、夜間モード時は点灯しません。
