import csv

import pandas as pd
import re
from _csv import Error, __version__, writer, reader, register_dialect, \
    unregister_dialect, get_dialect, list_dialects, \
    field_size_limit, \
    QUOTE_MINIMAL, QUOTE_ALL, QUOTE_NONNUMERIC, QUOTE_NONE, \
    __doc__
from _csv import Dialect as _Dialect

""""
brand_names = ['garanti-bbva']
db_name=""
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="1004cem+",

)
mycursor = mydb.cursor()

mycursor.execute("create database if  NOT EXISTS %s" % SIKAYET)
print(mydb)
mycursor.execute("create TABLE IF NOT EXISTS sikayet.sikayet_text (id INT AUTO_INCREMENT PRIMARY KEY,URL varchar(255),Title varchar(255),Description TEXT,Views_count varchar(9),Tags  TEXT, Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
"""
"""
def insert_data(val):


    sql = "INSERT INTO "+SIKAYET_TEXT_TABLE+"  (URL, Title, Description, Views_count, Tags, Time) VALUES  (%s, %s,%s,%s,%s,%s)"
    print(val)
    type(val)
    print(sql)
    mycursor.executemany(sql, val)

    mydb.commit()

    print(mycursor.rowcount, "was inserted.")
"""
headers = ['ID', 'Marka', 'Başlık', 'Açıklama', 'Tarih', 'Görüntüleme Sayısı', 'Etiketler']

def printFileXlsx(file_name, columns, result):
    flatten = lambda l: [item for sublist in l for item in sublist]
    df = pd.DataFrame(flatten(result), columns=columns)
    df.to_excel(file_name, index=False, encoding='utf-8')
"""

def writeFile(filename, open_type="a", result):
    with open(filename + ".csv", open_type, newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"')

        for row in result:
            writer.writerow(row)
        result.clear()
        csvfile.close()
"""