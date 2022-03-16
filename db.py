import mysql.connector as conn
import config

opt = {'host': config.DB_HOST, 'user': config.DB_USR, 'database': config.DB_NAME, 'password': config.DB_PASS}

try:
    db = conn.connect(**opt)
except conn.Error as e:
    print(e)