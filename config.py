import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
DB_USERNAME = str(os.getenv("DB_USERNAME"))
DB_PASSWORD = str(os.getenv("DB_PASSWORD"))
DATABASE = str(os.getenv("DATABASE"))
HOST = str(os.getenv("HOST"))
admins_id = [

]