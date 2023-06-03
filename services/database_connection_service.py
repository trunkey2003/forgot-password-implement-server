import os
import cx_Oracle as oracledb

def get_connection():
    return oracledb.connect(user=os.getenv("DATABASE_USERNAME"), password=os.getenv(
            "DATABASE_PASSWORD"), dsn=os.getenv("DATABASE_DSN"))