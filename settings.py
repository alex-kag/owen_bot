# Данный модуль читает настройки из файла конфигурации .env
import logging
import os

# для чтения конфигурационных файлов
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Нормальная работа
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger.info('Начато чтение конфига')
load_dotenv('.env')

try:
    API_TOKEN = os.getenv('token')
    URL_TO_GET_DATA = os.getenv('url_to_get_data')
    LOGIN = os.getenv('login')
    PASSWORD = os.getenv('password')

except:
    logger.critical("Не найден или некоректный файл настроек .env")
    exit(1)
