import os

from dotenv import load_dotenv

def get_database_url():
    load_dotenv()
    database_password = os.environ['DATABASE_PASSWORD']
    database_address = os.environ['DATABASE_ADDRESS']
    return f'postgresql://postgres:{database_password}@{database_address}/TodoApplicationDatabase'
