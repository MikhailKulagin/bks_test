import os

moex_url = os.getenv('MOEX_URL', 'http://iss.moex.com')
default_port = 8005
port = os.getenv('PORT', default_port)
db_name = os.getenv('DB_NAME', 'app_database_test_0')
default_try = 10
moex_try_count = os.getenv('MOEX_TRY_COUNT', default_try)
