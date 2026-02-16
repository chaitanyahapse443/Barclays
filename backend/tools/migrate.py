import os
from sqlalchemy import create_engine

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///./sar_ai.db')
engine = create_engine(DATABASE_URL)

def apply_schema():
    here = os.path.dirname(__file__)
    sql_file = os.path.join(here, '..', 'app', 'database', 'schema.sql')
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn = engine.connect()
    try:
        conn.execute(sql)
    finally:
        conn.close()

if __name__ == '__main__':
    apply_schema()
    print('Schema applied to', DATABASE_URL)
