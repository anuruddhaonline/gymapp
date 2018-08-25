import pymysql

def Connection():
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='',
                           db='face_final')
    c = conn.cursor()
    return c, conn