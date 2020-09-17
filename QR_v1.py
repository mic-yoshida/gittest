
import pymssql
import datetime
import ipget
import smtplib
from email.message import EmailMessage

## IP確認 ##
IP = ipget.ipget()   # 親機IP
BaseUnit = IP.ipaddr("wlan0")
# ----------------------------------------------------------------------------------------------------

## DB接続 ##
sv = 'yyg.japaneast.cloudapp.azure.com'
ip = '13.78.102.249'
db = 'VisualizetestDB'
un = 'sa'
pw = 'Takedan00yaj1'

cnxn = pymssql.connect(sv, un, pw, db)
cursor = cnxn.cursor()
# ----------------------------------------------------------------------------------------------------

## メール送信 ##
def sendMail(subject,myMessage):
    # 接続先 SMTP サーバの定義
    smtp = smtplib.SMTP('smtp.office365.com', 587)  # FQDN とポート番号

    # 認証情報の定義
    user = 'mic.rpa@mic-p.com'  # SMTP サーバに接続するためのユーザ
    password = "Mic12345"

    # メッセージの組み立て
    message = EmailMessage()
    message['From'] = user  # 送信者のメールアドレス
    message['To'] = 'yoshida.keisuke@mic-p.com'  # 受信者のメールアドレス
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


while True:
    try:

        BarcodeVal = input()                    # バーコードの情報
        Datetime = datetime.datetime.today()    # 日付

        if BarcodeVal[0] == "B":
            Count = input()
            cursor.execute(rf"INSERT INTO dbo.受注テスト VALUES('{BarcodeVal}', '{Count}' , '{Datetime}', '{BaseUnit}')")
        else:
            cursor.execute(rf"INSERT INTO dbo.QRコード VALUES('{BarcodeVal}', '{Datetime}', '{BaseUnit}')")
        
        cnxn.commit()

    except KeyboardInterrupt:
        cursor.close()
        cnxn.close()
        break

    except Exception as e:
        subject_text = ("【実行エラー】生産性見える化_QRリーダー")
        myMessage_text =f"【エラー内容】\n{e}\n\n 上記のエラーが発生いたしましたので、\n{BaseUnit} \n{Datetime}のレコードは登録されませんでした."
        sendMail(subject_text, myMessage_text)
        pass
