import logging
import asyncio
from aiogram.utils.exceptions import NetworkError
from services.setup_bot import dp, bot, storage, db
from bot.utils.logger import log_info
from bot.states.register_state import register_handlers


async def start_polling_with_retry():
    """Запуск polling с повторными попытками при ошибках сети."""
    retry_count = 5
    delay = 5
    for attempt in range(retry_count):
        try:
            await dp.start_polling()
            break
        except NetworkError as e:
            logging.error(f"Ошибка сети ({e}): попытка {attempt + 1} из {retry_count}.")
            if attempt < retry_count - 1:
                await asyncio.sleep(delay)
            else:
                logging.error("Не удалось подключиться к Telegram API после нескольких попыток.")
                break
        except Exception as e:
            logging.error(f"Неизвестная ошибка при запуске бота: {e}")
            break


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    log_info(f"DB instance: {db}")
    register_handlers(dp, db)
    
    
    try:
        await start_polling_with_retry()
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
    finally:
        await storage.close()
        await storage.wait_closed()
        await bot.close()