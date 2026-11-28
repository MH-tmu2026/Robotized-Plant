# Robotized Plant 実行マニュアル
Robotized Plantの実行マニュアルです。

## 使用デバイス
Robotized Plantの実行には、以下のデバイスを使用します。

- Raspberry Pi4（Raspberry pi OS Legacy, 64-bit）
- Grove Base Hat for Raspberry pi
- Depth AI カメラ（luxonis社製）
- TTP223（静電容量式タッチセンサ）
- Gravity:Analog Waterproof Capacitive Soil Moisture Sensor (土壌水分量センサ)
- Grove Water Sensor（水滴センサ）
- Grove Light Sensor v1.2（光センサ）
- WS2813RGBLEDStripWaterproof-30LED/m-1m（紐状LED）
- スピーカー


## 実行環境
動作環境はpython3.11.2、OpenRTM-aist2.1系です。
以下の手順で環境を整備します。

1. Raspberry pi4にOSをインストールする。
OpenRTMに対応しているRaspberry Pi OS のバージョン、Bookworm (64bit)をインストールします。
これは、[OpenRTM-aist公式webサイト](https://openrtm.org/ja/doc/installation/install_2_1/install_raspbian_2_1/)で案内されています。

2. Raspberry piの設定
I2C通信をオンにします。
また、時刻が同期していない場合、同期させます。

3. OpenRTM-aist Raspberry Pi OSパッケージをインストール
[OpenRTM-aist公式webサイト](https://openrtm.org/ja/doc/installation/install_2_1/install_raspbian_2_1/)に従い、OpenRTM-aistをインストールします。
サイト内の案内に従って、rtshellまでインストールを完了してください。
Raspberry pi4ではopenrtpが利用できないため、rtshellで操作を行います。

4. Grove.pyのインストール
[Grove Base Hat for Raspberry pi公式ウィキ](https://wiki.seeedstudio.com/ja/Grove_Base_Hat_for_Raspberry_Pi/)に従い、Grove.pyをインストールします。
pipに関連するエラーで弾かれる場合、3におけるrtshellのインストールも同様のエラーで失敗している可能性があるため、確認してください。

5. depthAI、blobconverterのインストール
[DepthAI公式ウェブサイト](https://docs.luxonis.com/software-v3/depthai/)に従い、depthAI、blobconverterの動作環境を整えてください。


## 実行方法
以下の手順で実行してください。

1. ターミナルを立ち上げ、それぞれのソースコードを実行する。
Control\_LED.pyはsudo権限をつけないと起動しない可能性があるため、sudo権限を付けて実行する。
2. コンポーネント操作用のターミナルを追加で立ち上げ、以下のようにポートの接続を行う。
```
rtcon /localhost/RasPi.host_cxt/Light_Sensor0.rtc:light /localhost/RasPi.host_cxt/Memory_State0.rtc:light
rtcon /localhost/RasPi.host_cxt/Soilmoisture_Sensor0.rtc:soilmoisture /localhost/RasPi.host_cxt/Memory_State0.rtc:soil
rtcon /localhost/RasPi.host_cxt/Leafmoisture_Sencor0.rtc:leafmoisture /localhost/RasPi.host_cxt/Memory_State0.rtc:leaf
rtcon /localhost/RasPi.host_cxt/Touch_Sensor0.rtc:touch /localhost/RasPi.host_cxt/Memory_State0.rtc:touch
rtcon /localhost/RasPi.host_cxt/Camera0.rtc:people /localhost/RasPi.host_cxt/Memory_State0.rtc:people

rtcon /localhost/RasPi.host_cxt/Memory_State0.rtc:state /localhost/RasPi.host_cxt/Make_trigger0.rtc:state
rtcon /localhost/RasPi.host_cxt/Memory_State0.rtc:state /localhost/RasPi.host_cxt/Q_Learning0.rtc:state

rtcon /localhost/RasPi.host_cxt/Make_trigger0.rtc:trigger /localhost/RasPi.host_cxt/Marcof0.rtc:trigger
rtcon /localhost/RasPi.host_cxt/Make_trigger0.rtc:trigger /localhost/RasPi.host_cxt/Play_Wav0.rtc:trigger
rtcon /localhost/RasPi.host_cxt/Marcof0.rtc:emotion /localhost/RasPi.host_cxt/Play_Wav0.rtc:emotion
rtcon /localhost/RasPi.host_cxt/Marcof0.rtc:emotion /localhost/RasPi.host_cxt/Control_LED0.rtc

rtcon /localhost/RasPi.host_cxt/Q_Learning0.rtc:action /localhost/RasPi.host_cxt/Play_Wav0.rtc:action
rtcon /localhost/RasPi.host_cxt/Play_Wav0.rtc:speech_event /localhost/RasPi.host_cxt/Q_Learning0.rtc:speech_event
```
3. 以下のように実行し、各コンポーネントを活性化させる。
```
rtact /localhost/RasPi.host_cxt/Light_Sensor0.rtc
rtact /localhost/RasPi.host_cxt/Soilmoisture_Sensor0.rtc
rtact /localhost/RasPi.host_cxt/Leafmoisture_Sencor0.rtc
rtact /localhost/RasPi.host_cxt/Touch_Sensor0.rtc
rtact /localhost/RasPi.host_cxt/Camera0.rtc 

rtact /localhost/RasPi.host_cxt/Play_Wav0.rtc
rtact /localhost/RasPi.host_cxt/Control_LED0.rtc
rtact /localhost/RasPi.host_cxt/Q_Learning0.rtc 
rtact /localhost/RasPi.host_cxt/Marcof0.rtc 
rtact /localhost/RasPi.host_cxt/Make_trigger0.rtc 
rtact /localhost/RasPi.host_cxt/Memory_State0.rtc  
```

## 終了方法
以下のように実行し、各コンポーネントを非活性化させてください。
```
rtdeact /localhost/RasPi.host_cxt/Memory_State0.rtc
rtdeact /localhost/RasPi.host_cxt/Control_LED0.rtc
rtdeact /localhost/RasPi.host_cxt/Make_trigger0.rtc 
rtdeact /localhost/RasPi.host_cxt/Marcof0.rtc 
rtdeact /localhost/RasPi.host_cxt/Q_Learning0.rtc 
rtdeact /localhost/RasPi.host_cxt/Play_Wav0.rtc

rtdeact /localhost/RasPi.host_cxt/Light_Sensor0.rtc
rtdeact /localhost/RasPi.host_cxt/Soilmoisture_Sensor0.rtc
rtdeact /localhost/RasPi.host_cxt/Leafmoisture_Sencor0.rtc
rtdeact /localhost/RasPi.host_cxt/Touch_Sensor0.rtc
rtdeact /localhost/RasPi.host_cxt/Camera0.rtc 
```
