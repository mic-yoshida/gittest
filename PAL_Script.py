#!/usr/bin/env python
# coding: UTF-8

#################################################################
# Copyright (C) 2017 Mono Wireless Inc. All Rights Reserved.    #
# Released under MW-SLA-*J,*E (MONO WIRELESS SOFTWARE LICENSE   #
# AGREEMENT).                                                   #
#################################################################

# ライブラリのインポート
import sys
import os
import threading
import time
import datetime
from optparse import *

import pymssql
import smtplib
import ipget
from email.message import EmailMessage


# WONO WIRELESSのシリアル電文パーサなどのAPIのインポート
sys.path.append('./MNLib/')
from apppal import AppPAL

# ここより下はグローバル変数の宣言
# コマンドラインオプションで使用する変数
options = None
args = None

# 各種フラグ
bEnableLog = False
bEnableErrMsg = False

# プログラムバージョン
Ver = "1.0.1"

def ParseArgs():
    global options, args

    parser = OptionParser()
    if os.name == 'nt':
        parser.add_option('-t', '--target', type='string', help='target for connection', dest='target', default='COM3')
    else:
        parser.add_option('-t', '--target', type='string', help='target for connection', dest='target', default='/dev/ttyUSB0')

    parser.add_option('-b', '--baud', dest='baud', type='int', help='baud rate for serial connection.', metavar='BAUD', default=115200)
    parser.add_option('-s', '--serialmode', dest='format', type='string', help='serial data format type. (Ascii or Binary)',  default='Ascii')
    parser.add_option('-l', '--log', dest='log', action='store_true', help='output log.', default=False)
    parser.add_option('-e', '--errormessage', dest='err', action='store_true', help='output error message.', default=False)
    (options, args) = parser.parse_args()


####################################################################################
## DB登録 ##
def DB_Output(DBDate,PALID):
    #親機IP取得
    IP = ipget.ipget()
    BaseUnit = IP.ipaddr("wlan0")
    # 開閉センサ
    if PALID == 1:
        #DB_string = ', '.join('?' * len(DBDate))
        #params = ['?' for item in DBDate]
        #query_string = "INSERT INTO dbo.開閉センサ VALUES (%s);" % (DB_string)
        #query_string = "INSERT INTO dbo.開閉センサ VALUES (%s);" % ','.join(params
        query_string = rf"INSERT INTO dbo.開閉センサ VALUES ('{DBDate['ArriveTime']}', {DBDate['LogicalID']}, '{DBDate['EndDeviceSID']}', '{DBDate['RouterSID']}', {DBDate['LQI']}, {DBDate['SequenceNumber']}, '{DBDate['Sensor']}', {DBDate['PALID']}, {DBDate['PALVersion']}, {DBDate['Power']}, {DBDate['ADC1']}, '{DBDate['HALLIC']}', '{BaseUnit}');"
    
    # 照度センサ
    elif PALID == 2:
        #DB_string = ', '.join('?' * len(DBDate))
        query_string = rf"INSERT INTO dbo.照度センサ VALUES ('{DBDate['ArriveTime']}', {DBDate['LogicalID']}, '{DBDate['EndDeviceSID']}', '{DBDate['RouterSID']}', {DBDate['LQI']}, {DBDate['SequenceNumber']}, '{DBDate['Sensor']}', {DBDate['PALID']}, {DBDate['PALVersion']}, {DBDate['Power']}, {DBDate['ADC1']}, {DBDate['Temperature']}, {DBDate['Humidity']}, {DBDate['Illuminance']}, '{BaseUnit}');"

    
    cursor.execute(query_string)
    


## メール送信 ##
def sendMail(subject,myMessage):
    # 接続先 SMTP サーバの定義
    smtp = smtplib.SMTP('smtp.office365.com', 587)  # FQDN とポート番号

    # 認証情報の定義
    user = 'mic.rpa@mic-p.com'  # SMTP サーバに接続するためのユーザ
    password = "Mic12345"
    #mail_list = ['akahira.serina@mic-p.com', 'yoshida.keisuke@mic-p.com', 'ota.yu@mic-p.com', 'tozato.uran@mic-p.com']
    mail_list = "yoshida.keisuke@mic-p.com"
    

    # メッセージの組み立て
    message = EmailMessage()
    message['From'] = user  # 送信者のメールアドレス
    #message['To'] = 'akahira.serina@mic-p.com'  # 受信者のメールアドレス
    message['To'] = mail_list
    message['Subject'] = subject  # 件名
    message.set_content(myMessage)  # 本文

    # SMTP サーバへの接続とメールの送信
    smtp.ehlo()
        # (250, ...
    smtp.starttls()  # TLS の開始（以降の通信は暗号化される）
        # (220, b'2.0.0 SMTP server ready')
    smtp.ehlo()
        # (250, ...
    smtp.login(user, password)  # SMTP サーバにログイン
        # (235, ...
    smtp.send_message(message)  # メッセージの送信
        # {}
    smtp.quit()  # SMTP セッションの終了と TCP コネクションの切断
        # (221, b'2.0.0 Service closing transmission channel')

####################################################################################
# ----------------------------------------------------------------------------------------------------
# DB接続
# ----------------------------------------------------------------------------------------------------
sv = 'yyg.japaneast.cloudapp.azure.com'
ip = '13.78.102.249'
db = 'VisualizetestDB'
un = 'sa'
pw = 'Takedan00yaj1'

cnxn = pymssql.connect(sv, un, pw, db)
cursor = cnxn.cursor()
########################################################################################################

## 実行 ##
if __name__ == '__main__':
    #print("*** MONOWIRELESS App_PAL_Viewer " + Ver + " ***")

    ParseArgs()

    bEnableLog = options.log
    bEnableErrMsg = options.err
    try:
        PAL = AppPAL(port=options.target, baud=options.baud, tout=0.05, sformat=options.format, err=bEnableErrMsg)
    except:
        print("Cannot open \"AppPAL\" class...")
        exit(1)

    while True:
        try:
            # データがあるかどうかの確認
            if PAL.ReadSensorData():
                # あったら辞書を取得する
                Data = PAL.GetDataDict()

                # なにか処理を記述する場合はこの下に書く
                print(Data)         # 受け取った辞書をそのまま標準出力する
                

                # DB登録用データ辞書を値だけのリストにする
                DBOutlist = PAL.DBCreateOutputDict()
                # センサIDを格納
                PALID_Data = PAL.GetDataDict_PALID()
                # DB登録関数呼び出し
                DB_Output(DBOutlist, PALID_Data)

                cnxn.commit()
                
                # ログを出力するオプションが有効だったらログを出力する。
                if bEnableLog == True:
                    PAL.OutputCSV() # CSVでログをとる

        # Ctrl+C でこのスクリプトを抜ける
        except KeyboardInterrupt:
            cursor.close()
            cnxn.close()
            break

        except Exception as e:
            subject_text = ("【実行エラー】生産性見える化")
            myMessage_text =f"【エラー内容】\n{e}\n\n 上記のエラーが発生いたしましたので、{DBOutlist['ArriveTime']}のレコードは登録されませんでした."
            sendMail(subject_text, myMessage_text)
            pass

    del PAL

    #print("*** Exit App_PAL Viewer ***")
