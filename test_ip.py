import ipget
import datetime

Datetime = datetime.datetime.today()    # 日付
IP = ipget.ipget()   # 親機IPよ
BaseUnit = IP.ipaddr("wlan0")

print(Datetime)
print(BaseUnit)
