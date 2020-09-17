import pymssql
 
sv = 'yygtest01.japaneast.cloudapp.azure.com'
ip = '13.78.102.249'
db = 'VisualizetestDB'
un = 'sa'
pw = 'Takedan00yaj1'

DBDate = ['2020/08/27 11:12:15.936', 8, '2014E07', 'No Relay', 117, 1183, 'PAL', 1, 1, 2315, 788, 'Close(S)', 'parent']
DB_string = ', '.join('?' * len(DBDate))

conn = pymssql.connect(sv, un, pw, db)
cur = conn.cursor()
cur.execute("INSERT INTO dbo.開閉センサ VALUES('2020/08/27 11:12:15.936', 8, '2014E07', 'No Relay', 117, 1183, 'PAL', 1, 1, 2315, 788, 'Close(S)', 'parent')")

conn.commit()
cur.close()
conn.close()